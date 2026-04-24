"""Доменный сервис для работы с PDF.

Операции:
  - merge: объединение нескольких PDF в один (pypdf + fallback pikepdf)
  - split_per_page / split_by_ranges: разделение PDF
  - parse_ranges: парсинг текста диапазонов ("1-5, 7, 10-12")
  - compress: сжатие через ghostscript (subprocess)
  - set_password / remove_password: шифрование/дешифрование
  - pdf_to_images / images_to_pdf: конвертация PDF <-> изображения
  - extract_text: извлечение текста
  - get_page_count / is_encrypted

Все блокирующие операции через asyncio.to_thread().
Глобальный семафор _SEM ограничивает число одновременных операций.
"""
from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path

from PIL import Image
import pikepdf
import pypdf
from pypdf.errors import PyPdfError, FileNotDecryptedError, DependencyError

logger = logging.getLogger(__name__)

# ограничиваем параллельные PDF-операции (каждая ест CPU/RAM)
_SEM = asyncio.Semaphore(3)

# уровни сжатия ghostscript -> pdfsettings
_GS_LEVELS = {
    "low": "/printer",     # качество выше, сжатие меньше
    "medium": "/ebook",    # баланс
    "high": "/screen",     # максимальное сжатие
}


# === Исключения ===


class PdfReadError(Exception):
    """PDF битый и не читается ни через pypdf, ни через pikepdf."""


class PdfEncryptedError(Exception):
    """PDF защищён паролем — операция невозможна без дешифровки."""


class InvalidPassword(Exception):
    """Неверный пароль при попытке снять защиту."""


class InvalidRangeError(ValueError):
    """Невалидный диапазон страниц."""


# === Вспомогательные (синхронные) функции ===


def _sync_get_page_count(pdf_path: Path) -> int:
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        if reader.is_encrypted:
            raise PdfEncryptedError("PDF защищён паролем")
        return len(reader.pages)
    except PdfEncryptedError:
        raise
    except PyPdfError:
        # пробуем pikepdf как fallback
        try:
            with pikepdf.open(str(pdf_path)) as pdf:
                return len(pdf.pages)
        except pikepdf.PasswordError as e:
            raise PdfEncryptedError("PDF защищён паролем") from e
        except Exception as e:
            raise PdfReadError(f"Не удалось прочитать PDF: {e}") from e
    except Exception as e:
        raise PdfReadError(f"Не удалось прочитать PDF: {e}") from e


def _sync_is_encrypted(pdf_path: Path) -> bool:
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        return bool(reader.is_encrypted)
    except Exception:
        # если pypdf упал, пробуем pikepdf
        try:
            with pikepdf.open(str(pdf_path)) as _:
                return False
        except pikepdf.PasswordError:
            return True
        except Exception as e:
            raise PdfReadError(f"Не удалось прочитать PDF: {e}") from e


def _sync_merge(pdf_paths: list[Path], output: Path) -> None:
    """Сначала pypdf, при ошибке — pikepdf."""
    try:
        writer = pypdf.PdfWriter()
        for p in pdf_paths:
            reader = pypdf.PdfReader(str(p))
            if reader.is_encrypted:
                raise PdfEncryptedError(f"Файл {p.name} защищён паролем")
            for page in reader.pages:
                writer.add_page(page)
        with open(output, "wb") as f:
            writer.write(f)
        writer.close()
        return
    except PdfEncryptedError:
        raise
    except PyPdfError as e:
        logger.warning("pypdf merge упал, пробуем pikepdf: %s", e)

    # fallback pikepdf
    try:
        dst = pikepdf.Pdf.new()
        for p in pdf_paths:
            try:
                with pikepdf.open(str(p)) as src:
                    dst.pages.extend(src.pages)
            except pikepdf.PasswordError as e:
                raise PdfEncryptedError(f"Файл {p.name} защищён паролем") from e
        dst.save(str(output))
        dst.close()
    except PdfEncryptedError:
        raise
    except Exception as e:
        raise PdfReadError(f"Не удалось объединить PDF: {e}") from e


def _sync_split_per_page(pdf_path: Path, output_dir: Path) -> list[Path]:
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        if reader.is_encrypted:
            raise PdfEncryptedError("PDF защищён паролем")
        result: list[Path] = []
        for i, page in enumerate(reader.pages, start=1):
            writer = pypdf.PdfWriter()
            writer.add_page(page)
            out = output_dir / f"page_{i:03d}.pdf"
            with open(out, "wb") as f:
                writer.write(f)
            writer.close()
            result.append(out)
        return result
    except PdfEncryptedError:
        raise
    except PyPdfError as e:
        logger.warning("pypdf split упал, пробуем pikepdf: %s", e)

    # fallback pikepdf
    try:
        with pikepdf.open(str(pdf_path)) as src:
            result = []
            for i, page in enumerate(src.pages, start=1):
                dst = pikepdf.Pdf.new()
                dst.pages.append(page)
                out = output_dir / f"page_{i:03d}.pdf"
                dst.save(str(out))
                dst.close()
                result.append(out)
            return result
    except pikepdf.PasswordError as e:
        raise PdfEncryptedError("PDF защищён паролем") from e
    except Exception as e:
        raise PdfReadError(f"Не удалось разделить PDF: {e}") from e


def _sync_split_by_ranges(
    pdf_path: Path, ranges: list[tuple[int, int]], output_dir: Path
) -> list[Path]:
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        if reader.is_encrypted:
            raise PdfEncryptedError("PDF защищён паролем")
        page_count = len(reader.pages)
        result: list[Path] = []
        for idx, (start, end) in enumerate(ranges, start=1):
            if start < 1 or end > page_count or start > end:
                raise InvalidRangeError(
                    f"Диапазон {start}-{end} вне [1; {page_count}]"
                )
            writer = pypdf.PdfWriter()
            for page_num in range(start, end + 1):
                writer.add_page(reader.pages[page_num - 1])
            out = output_dir / f"range_{idx:02d}_{start}-{end}.pdf"
            with open(out, "wb") as f:
                writer.write(f)
            writer.close()
            result.append(out)
        return result
    except (PdfEncryptedError, InvalidRangeError):
        raise
    except PyPdfError as e:
        logger.warning("pypdf split_ranges упал, пробуем pikepdf: %s", e)

    # fallback pikepdf
    try:
        with pikepdf.open(str(pdf_path)) as src:
            page_count = len(src.pages)
            result = []
            for idx, (start, end) in enumerate(ranges, start=1):
                if start < 1 or end > page_count or start > end:
                    raise InvalidRangeError(
                        f"Диапазон {start}-{end} вне [1; {page_count}]"
                    )
                dst = pikepdf.Pdf.new()
                for page_num in range(start, end + 1):
                    dst.pages.append(src.pages[page_num - 1])
                out = output_dir / f"range_{idx:02d}_{start}-{end}.pdf"
                dst.save(str(out))
                dst.close()
                result.append(out)
            return result
    except pikepdf.PasswordError as e:
        raise PdfEncryptedError("PDF защищён паролем") from e
    except InvalidRangeError:
        raise
    except Exception as e:
        raise PdfReadError(f"Не удалось разделить PDF: {e}") from e


def _sync_set_password(pdf_path: Path, output: Path, password: str) -> None:
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        if reader.is_encrypted:
            raise PdfEncryptedError("PDF уже защищён паролем")
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(user_password=password, owner_password=password)
        with open(output, "wb") as f:
            writer.write(f)
        writer.close()
    except PdfEncryptedError:
        raise
    except PyPdfError as e:
        # fallback pikepdf
        try:
            with pikepdf.open(str(pdf_path)) as src:
                src.save(
                    str(output),
                    encryption=pikepdf.Encryption(
                        owner=password, user=password, R=4
                    ),
                )
        except pikepdf.PasswordError as pe:
            raise PdfEncryptedError("PDF уже защищён паролем") from pe
        except Exception as ex:
            raise PdfReadError(f"Не удалось зашифровать: {ex}") from e


def _sync_remove_password(pdf_path: Path, output: Path, password: str) -> None:
    # пробуем pypdf
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        if reader.is_encrypted:
            ok = reader.decrypt(password)
            if not ok:
                raise InvalidPassword("Неверный пароль")
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(output, "wb") as f:
            writer.write(f)
        writer.close()
        return
    except InvalidPassword:
        raise
    except (FileNotDecryptedError, DependencyError):
        pass  # fallback ниже
    except PyPdfError as e:
        logger.warning("pypdf decrypt упал, пробуем pikepdf: %s", e)
    except Exception as e:
        logger.warning("неизвестная ошибка pypdf decrypt, пробуем pikepdf: %s", e)

    # fallback pikepdf
    try:
        with pikepdf.open(str(pdf_path), password=password) as src:
            src.save(str(output))
    except pikepdf.PasswordError as e:
        raise InvalidPassword("Неверный пароль") from e
    except Exception as e:
        raise PdfReadError(f"Не удалось снять пароль: {e}") from e


def _sync_pdf_to_images(
    pdf_path: Path, output_dir: Path, dpi: int
) -> list[Path]:
    # pdf2image требует poppler — импортируем лениво
    from pdf2image import convert_from_path

    try:
        # output_folder + paths_only — pdf2image пишет страницы на диск
        # по мере рендеринга, а не держит все PIL-объекты в RAM одновременно
        paths = convert_from_path(
            str(pdf_path),
            dpi=dpi,
            fmt="png",
            output_folder=str(output_dir),
            paths_only=True,
        )
    except Exception as e:
        # распространённый признак защищённого PDF
        msg = str(e).lower()
        if "password" in msg or "encrypted" in msg:
            raise PdfEncryptedError("PDF защищён паролем") from e
        raise PdfReadError(f"Не удалось отрендерить PDF: {e}") from e

    return [Path(p) for p in paths]


def _sync_images_to_pdf(image_paths: list[Path], output: Path) -> None:
    if not image_paths:
        raise ValueError("Нет изображений")
    pil_images: list[Image.Image] = []
    try:
        for p in image_paths:
            img = Image.open(str(p))
            # PDF не умеет не-RGB — приводим всё к RGB разом
            if img.mode != "RGB":
                img = img.convert("RGB")
            pil_images.append(img)
        first = pil_images[0]
        rest = pil_images[1:]
        first.save(
            str(output),
            format="PDF",
            save_all=True,
            append_images=rest,
        )
    finally:
        for img in pil_images:
            try:
                img.close()
            except Exception:
                pass


def _sync_extract_text(pdf_path: Path) -> str:
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        if reader.is_encrypted:
            raise PdfEncryptedError("PDF защищён паролем")
        parts: list[str] = []
        for page in reader.pages:
            try:
                text = page.extract_text() or ""
            except Exception as e:
                logger.warning("Страница не извлеклась: %s", e)
                text = ""
            parts.append(text)
        return "\n\n".join(parts).strip()
    except PdfEncryptedError:
        raise
    except PyPdfError as e:
        raise PdfReadError(f"Не удалось извлечь текст: {e}") from e
    except Exception as e:
        raise PdfReadError(f"Не удалось извлечь текст: {e}") from e


# === Публичное API (async) ===


class PdfService:
    """Фасад для всех PDF-операций. Все методы асинхронные."""

    @staticmethod
    def parse_ranges(text: str, page_count: int) -> list[tuple[int, int]]:
        """Парсит строку вида "1-5, 7, 10-12" в список (start, end).

        Валидирует:
          - непустой ввод
          - каждый диапазон вида "N" или "N-M"
          - все числа в [1; page_count]
          - start <= end

        Raises InvalidRangeError при любой ошибке.
        """
        if not text or not text.strip():
            raise InvalidRangeError("Пустой ввод")

        result: list[tuple[int, int]] = []
        parts = [p.strip() for p in text.split(",") if p.strip()]
        if not parts:
            raise InvalidRangeError("Нет диапазонов")

        range_re = re.compile(r"^(\d+)(?:\s*-\s*(\d+))?$")
        for part in parts:
            m = range_re.match(part)
            if not m:
                raise InvalidRangeError(f"Неверный формат: {part!r}")
            start = int(m.group(1))
            end = int(m.group(2)) if m.group(2) else start
            if start < 1 or end < 1:
                raise InvalidRangeError(f"Страница < 1 в {part!r}")
            if start > end:
                raise InvalidRangeError(
                    f"Начало больше конца в {part!r}"
                )
            if end > page_count:
                raise InvalidRangeError(
                    f"Страница {end} > {page_count} (всего страниц в PDF)"
                )
            result.append((start, end))
        return result

    @staticmethod
    async def get_page_count(pdf_path: Path) -> int:
        async with _SEM:
            return await asyncio.to_thread(_sync_get_page_count, pdf_path)

    @staticmethod
    async def is_encrypted(pdf_path: Path) -> bool:
        async with _SEM:
            return await asyncio.to_thread(_sync_is_encrypted, pdf_path)

    @staticmethod
    async def merge(pdf_paths: list[Path], output: Path) -> None:
        async with _SEM:
            await asyncio.to_thread(_sync_merge, pdf_paths, output)

    @staticmethod
    async def split_per_page(
        pdf_path: Path, output_dir: Path
    ) -> list[Path]:
        async with _SEM:
            return await asyncio.to_thread(
                _sync_split_per_page, pdf_path, output_dir
            )

    @staticmethod
    async def split_by_ranges(
        pdf_path: Path,
        ranges: list[tuple[int, int]],
        output_dir: Path,
    ) -> list[Path]:
        async with _SEM:
            return await asyncio.to_thread(
                _sync_split_by_ranges, pdf_path, ranges, output_dir
            )

    @staticmethod
    async def compress(
        pdf_path: Path, output: Path, level: str = "medium"
    ) -> None:
        """Сжатие через ghostscript CLI."""
        if level not in _GS_LEVELS:
            raise ValueError(f"Unknown level: {level}")
        pdf_setting = _GS_LEVELS[level]

        async with _SEM:
            proc = await asyncio.create_subprocess_exec(
                "gs",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS={pdf_setting}",
                "-dNOPAUSE",
                "-dBATCH",
                "-dQUIET",
                f"-sOutputFile={output}",
                str(pdf_path),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                _, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=120
                )
            except asyncio.TimeoutError:
                # ghostscript завис — убиваем и рапортуем
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                try:
                    await proc.wait()
                except Exception:
                    pass
                raise PdfReadError("ghostscript timeout")
            if proc.returncode != 0 or not output.exists():
                err = (stderr or b"").decode("utf-8", errors="replace")[:500]
                raise PdfReadError(f"ghostscript упал: {err}")

    @staticmethod
    async def set_password(
        pdf_path: Path, output: Path, password: str
    ) -> None:
        async with _SEM:
            await asyncio.to_thread(
                _sync_set_password, pdf_path, output, password
            )

    @staticmethod
    async def remove_password(
        pdf_path: Path, output: Path, password: str
    ) -> None:
        async with _SEM:
            await asyncio.to_thread(
                _sync_remove_password, pdf_path, output, password
            )

    @staticmethod
    async def pdf_to_images(
        pdf_path: Path, output_dir: Path, dpi: int = 150
    ) -> list[Path]:
        async with _SEM:
            return await asyncio.to_thread(
                _sync_pdf_to_images, pdf_path, output_dir, dpi
            )

    @staticmethod
    async def images_to_pdf(
        image_paths: list[Path], output: Path
    ) -> None:
        async with _SEM:
            await asyncio.to_thread(
                _sync_images_to_pdf, image_paths, output
            )

    @staticmethod
    async def extract_text(pdf_path: Path) -> str:
        async with _SEM:
            return await asyncio.to_thread(_sync_extract_text, pdf_path)


# готовый экземпляр
pdf_service = PdfService()
