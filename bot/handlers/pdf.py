"""PDF-хэндлеры: полная FSM-логика для 7 операций.

Операции (callback_data меню):
  pdf:merge       — склеить PDF
  pdf:split       — разделить PDF
  pdf:compress    — сжать
  pdf:password    — установить/снять пароль
  pdf:to_images   — PDF → картинки
  pdf:from_images — картинки → PDF
  pdf:extract     — извлечь текст

Временные файлы хранятся в директории tempfile.mkdtemp(prefix="pdfbot_"),
путь сохраняется в FSM-state (ключ "tmp_dir"). На cancel / завершении FSM —
удаляем папку рекурсивно. Сироты после SIGKILL чистятся на старте бота.
"""
from __future__ import annotations

import asyncio
import logging
import shutil
import tempfile
import zipfile
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    FSInputFile,
    Message,
)

from bot.database import async_session
from bot.database.crud import get_user_language
from bot.i18n import t
from bot.keyboards.inline import (
    get_cancel_only,
    get_compress_levels,
    get_confirm_large,
    get_images_controls,
    get_merge_controls,
    get_password_actions,
    get_pdf_menu_keyboard,
    get_quality_levels,
    get_split_mode,
)
from bot.services.pdf import (
    InvalidPassword,
    InvalidRangeError,
    PdfEncryptedError,
    PdfReadError,
    pdf_service,
)

logger = logging.getLogger(__name__)
router = Router()

from bot.config import settings

# Local Bot API снимает лимиты: 2 ГБ вместо 20 МБ на вход и 49 МБ на выход.
_IS_LOCAL_API = settings.bot_api_url != "https://api.telegram.org"
MAX_INPUT_MB = 1999 if _IS_LOCAL_API else 20
MAX_OUTPUT_MB = 1999 if _IS_LOCAL_API else 49
MAX_FILE_SIZE = MAX_INPUT_MB * 1024 * 1024
MAX_UPLOAD_SIZE = MAX_OUTPUT_MB * 1024 * 1024
LARGE_PDF_THRESHOLD = 50  # страниц


# === FSM-группы ===


class MergeStates(StatesGroup):
    collecting_files = State()


class SplitStates(StatesGroup):
    waiting_file = State()
    waiting_mode = State()
    waiting_ranges = State()


class CompressStates(StatesGroup):
    waiting_file = State()
    waiting_level = State()


class PasswordStates(StatesGroup):
    waiting_file = State()
    waiting_action = State()
    waiting_password_set = State()
    waiting_password_remove = State()


class PdfToImagesStates(StatesGroup):
    waiting_file = State()
    waiting_confirm_large = State()
    waiting_quality = State()


class ImagesToPdfStates(StatesGroup):
    collecting_images = State()


class ExtractTextStates(StatesGroup):
    waiting_file = State()


# === Утилиты ===


async def _lang(user_id: int) -> str:
    async with async_session() as session:
        return await get_user_language(session, user_id)


def _make_tmp_dir() -> Path:
    """Создаёт временную директорию на диске.

    Используем mkdtemp (а не TemporaryDirectory), чтобы НЕ зависеть от
    живого объекта в памяти: при SIGKILL процесса ничего не утечёт —
    на старте бота выметается всё `pdfbot_*` в tmp.
    """
    return Path(tempfile.mkdtemp(prefix="pdfbot_"))


def _make_tmp_dir_in_state(state_data: dict) -> Path:
    """Создаёт tmp-директорию и кладёт путь в state_data["tmp_dir"]."""
    path = _make_tmp_dir()
    state_data["tmp_dir"] = str(path)
    return path


def _cleanup_tmp(tmp_path_str: str | None) -> None:
    """Удаляет временную директорию со всем содержимым."""
    if tmp_path_str:
        shutil.rmtree(tmp_path_str, ignore_errors=True)


async def _download_and_purge(bot, file_obj, destination: Path) -> None:
    """Скачивает файл в destination и сразу сносит исходник из bot-api volume.

    С Local Bot API исходник лежит в /var/lib/telegram-bot-api/<token>/...
    aiogram копирует в destination, но исходник остаётся — мы его вручную удаляем.
    Для облачного Bot API file_path — URL, никакого локального файла нет, тогда
    просто делаем обычный download.
    """
    if _IS_LOCAL_API:
        file = await bot.get_file(file_obj.file_id)
        src = file.file_path
        if src and Path(src).is_file():
            shutil.copy2(src, destination)
            try:
                Path(src).unlink()
            except OSError as e:
                logger.warning("Не удалось удалить исходник %s: %s", src, e)
            return
    # fallback: облачный API или исходника нет (тогда download() вытащит по URL)
    await bot.download(file_obj, destination=destination)


async def _clear_state_and_tmp(state: FSMContext) -> None:
    data = await state.get_data()
    _cleanup_tmp(data.get("tmp_dir"))
    await state.clear()


async def _finish_ok(target: Message | CallbackQuery, state: FSMContext, lang: str) -> None:
    """Чистит state/tmp и показывает главное PDF-меню после успешной операции."""
    await _clear_state_and_tmp(state)
    msg = target.message if isinstance(target, CallbackQuery) else target
    await msg.answer(
        t("pdf.menu", lang),
        reply_markup=get_pdf_menu_keyboard(lang),
        parse_mode="HTML",
    )


def _human_mb(size_bytes: int) -> str:
    return f"{size_bytes / (1024 * 1024):.2f}"


async def _download_pdf(
    message: Message, tmp_dir: Path, lang: str
) -> Path | None:
    """Проверяет что это PDF разумного размера и скачивает в tmp_dir.

    Возвращает путь к файлу или None (+ отправляет сообщение об ошибке).
    При ошибке сам НИЧЕГО не чистит — за tmp_dir отвечает вызывающий код,
    т.к. для Merge/Images один tmp_dir переиспользуется для нескольких файлов.
    """
    doc = message.document
    if not doc:
        await message.answer(t("error.not_pdf", lang), parse_mode="HTML")
        return None
    # mime может быть None для «application/octet-stream» → проверяем ещё расширение
    is_pdf_mime = (doc.mime_type or "").lower() == "application/pdf"
    is_pdf_ext = (doc.file_name or "").lower().endswith(".pdf")
    if not (is_pdf_mime or is_pdf_ext):
        await message.answer(t("error.not_pdf", lang), parse_mode="HTML")
        return None
    if doc.file_size and doc.file_size > MAX_FILE_SIZE:
        await message.answer(
            t("error.file_too_large", lang, max_mb=MAX_INPUT_MB), parse_mode="HTML"
        )
        return None

    # уникальное имя, чтобы не перезатирали друг друга
    suffix = Path(doc.file_name or "file.pdf").suffix or ".pdf"
    dest = tmp_dir / f"{doc.file_unique_id}{suffix}"
    status = await message.answer(t("status.downloading", lang), parse_mode="HTML")
    try:
        await _download_and_purge(message.bot, doc, dest)
    except Exception as e:
        logger.exception("Ошибка скачивания: %s", e)
        try:
            await status.edit_text(t("error.generic", lang), parse_mode="HTML")
        except Exception:
            pass
        # чистим битый файл если частично скачался
        try:
            if dest.exists():
                dest.unlink()
        except Exception:
            pass
        return None
    try:
        await status.delete()
    except Exception:
        pass
    return dest


async def _handle_pdf_error(
    message: Message, exc: Exception, lang: str
) -> None:
    if isinstance(exc, PdfEncryptedError):
        await message.answer(t("error.pdf_encrypted", lang), parse_mode="HTML")
    elif isinstance(exc, PdfReadError):
        await message.answer(t("error.pdf_read_failed", lang), parse_mode="HTML")
    else:
        logger.exception("Неожиданная ошибка в PDF: %s", exc)
        await message.answer(t("error.generic", lang), parse_mode="HTML")


# === Общие callbacks ===


@router.callback_query(F.data == "cancel_op")
async def cb_cancel_op(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(callback.from_user.id)
    await _clear_state_and_tmp(state)
    try:
        await callback.message.edit_text(
            t("error.operation_cancelled", lang),
            parse_mode="HTML",
        )
    except Exception:
        await callback.message.answer(
            t("error.operation_cancelled", lang), parse_mode="HTML"
        )
    # возвращаем в главное меню
    await callback.message.answer(
        t("pdf.menu", lang),
        reply_markup=get_pdf_menu_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# === Запуск операций из меню ===


@router.callback_query(F.data == "pdf:merge")
async def cb_start_merge(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(callback.from_user.id)
    await _clear_state_and_tmp(state)

    data: dict = {}
    _make_tmp_dir_in_state(data)
    data["files"] = []
    await state.set_state(MergeStates.collecting_files)
    await state.update_data(**data)

    await callback.message.edit_text(
        t("pdf.merge.prompt", lang),
        reply_markup=get_cancel_only(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "pdf:split")
async def cb_start_split(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(callback.from_user.id)
    await _clear_state_and_tmp(state)

    data: dict = {}
    _make_tmp_dir_in_state(data)
    await state.set_state(SplitStates.waiting_file)
    await state.update_data(**data)

    await callback.message.edit_text(
        t("pdf.split.prompt_file", lang),
        reply_markup=get_cancel_only(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "pdf:compress")
async def cb_start_compress(
    callback: CallbackQuery, state: FSMContext
) -> None:
    lang = await _lang(callback.from_user.id)
    await _clear_state_and_tmp(state)

    data: dict = {}
    _make_tmp_dir_in_state(data)
    await state.set_state(CompressStates.waiting_file)
    await state.update_data(**data)

    await callback.message.edit_text(
        t("pdf.compress.prompt_file", lang),
        reply_markup=get_cancel_only(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "pdf:password")
async def cb_start_password(
    callback: CallbackQuery, state: FSMContext
) -> None:
    lang = await _lang(callback.from_user.id)
    await _clear_state_and_tmp(state)

    data: dict = {}
    _make_tmp_dir_in_state(data)
    await state.set_state(PasswordStates.waiting_file)
    await state.update_data(**data)

    await callback.message.edit_text(
        t("pdf.password.prompt_file", lang),
        reply_markup=get_cancel_only(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "pdf:to_images")
async def cb_start_to_images(
    callback: CallbackQuery, state: FSMContext
) -> None:
    lang = await _lang(callback.from_user.id)
    await _clear_state_and_tmp(state)

    data: dict = {}
    _make_tmp_dir_in_state(data)
    await state.set_state(PdfToImagesStates.waiting_file)
    await state.update_data(**data)

    await callback.message.edit_text(
        t("pdf.to_images.prompt_file", lang),
        reply_markup=get_cancel_only(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "pdf:from_images")
async def cb_start_from_images(
    callback: CallbackQuery, state: FSMContext
) -> None:
    lang = await _lang(callback.from_user.id)
    await _clear_state_and_tmp(state)

    data: dict = {}
    _make_tmp_dir_in_state(data)
    data["images"] = []
    await state.set_state(ImagesToPdfStates.collecting_images)
    await state.update_data(**data)

    await callback.message.edit_text(
        t("pdf.from_images.prompt", lang),
        reply_markup=get_cancel_only(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "pdf:extract")
async def cb_start_extract(
    callback: CallbackQuery, state: FSMContext
) -> None:
    lang = await _lang(callback.from_user.id)
    await _clear_state_and_tmp(state)

    data: dict = {}
    _make_tmp_dir_in_state(data)
    await state.set_state(ExtractTextStates.waiting_file)
    await state.update_data(**data)

    await callback.message.edit_text(
        t("pdf.extract.prompt", lang),
        reply_markup=get_cancel_only(lang),
        parse_mode="HTML",
    )
    await callback.answer()


# === MERGE ===


@router.message(MergeStates.collecting_files, F.document)
async def merge_on_pdf(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id)
    data = await state.get_data()
    tmp_dir = Path(data["tmp_dir"])

    pdf_path = await _download_pdf(message, tmp_dir, lang)
    if not pdf_path:
        return

    # проверяем что PDF не зашифрован — merge с паролем не работает,
    # лучше отсечь сразу и не тащить до фактического объединения
    try:
        encrypted = await pdf_service.is_encrypted(pdf_path)
    except Exception as e:
        await _handle_pdf_error(message, e, lang)
        try:
            pdf_path.unlink()
        except Exception:
            pass
        return

    if encrypted:
        try:
            pdf_path.unlink()
        except Exception:
            pass
        fname = message.document.file_name or "PDF"
        await message.answer(
            t("error.pdf_encrypted", lang) + f"\n\n<code>{fname}</code>",
            parse_mode="HTML",
        )
        return

    files: list[str] = list(data.get("files", []))
    files.append(str(pdf_path))
    await state.update_data(files=files)

    can_merge = len(files) >= 2
    await message.answer(
        t("pdf.merge.received", lang, count=len(files)),
        reply_markup=get_merge_controls(lang, can_merge=can_merge),
        parse_mode="HTML",
    )


@router.callback_query(MergeStates.collecting_files, F.data == "merge:add_more")
async def merge_add_more(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(callback.from_user.id)
    await callback.answer()
    await callback.message.answer(
        t("pdf.merge.need_more", lang), parse_mode="HTML"
    )


@router.callback_query(MergeStates.collecting_files, F.data == "merge:do")
async def merge_do(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(callback.from_user.id)
    data = await state.get_data()
    files: list[str] = data.get("files", [])
    tmp_dir = Path(data["tmp_dir"])

    if len(files) < 2:
        await callback.answer(t("error.need_min_2", lang), show_alert=True)
        return

    await callback.answer()
    status = await callback.message.answer(
        t("pdf.merge.processing", lang, count=len(files)),
        parse_mode="HTML",
    )

    output = tmp_dir / "merged.pdf"
    try:
        await pdf_service.merge([Path(p) for p in files], output)
    except Exception as e:
        await _handle_pdf_error(callback.message, e, lang)
        await _clear_state_and_tmp(state)
        return

    try:
        await status.edit_text(
            t("pdf.merge.done", lang, count=len(files)),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await callback.message.answer_document(
        FSInputFile(output, filename="merged.pdf"),
    )
    await _finish_ok(callback, state, lang)


# === SPLIT ===


@router.message(SplitStates.waiting_file, F.document)
async def split_on_pdf(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id)
    data = await state.get_data()
    tmp_dir = Path(data["tmp_dir"])

    pdf_path = await _download_pdf(message, tmp_dir, lang)
    if not pdf_path:
        return

    # узнаём количество страниц
    try:
        pages = await pdf_service.get_page_count(pdf_path)
    except Exception as e:
        await _handle_pdf_error(message, e, lang)
        await _clear_state_and_tmp(state)
        return

    await state.update_data(pdf_path=str(pdf_path), pages=pages)
    await state.set_state(SplitStates.waiting_mode)
    await message.answer(
        t("pdf.split.prompt_mode", lang, pages=pages),
        reply_markup=get_split_mode(lang),
        parse_mode="HTML",
    )


@router.callback_query(SplitStates.waiting_mode, F.data == "split:per_page")
async def split_per_page(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(callback.from_user.id)
    data = await state.get_data()
    pdf_path = Path(data["pdf_path"])
    tmp_dir = Path(data["tmp_dir"])

    await callback.answer()
    status = await callback.message.answer(
        t("pdf.split.processing", lang), parse_mode="HTML"
    )

    out_dir = tmp_dir / "split_pages"
    out_dir.mkdir(exist_ok=True)
    try:
        files = await pdf_service.split_per_page(pdf_path, out_dir)
    except Exception as e:
        await _handle_pdf_error(callback.message, e, lang)
        await _clear_state_and_tmp(state)
        return

    zip_path = tmp_dir / "pages.zip"
    await _zip_files(files, zip_path)

    if zip_path.stat().st_size >= MAX_UPLOAD_SIZE:
        try:
            await status.delete()
        except Exception:
            pass
        await callback.message.answer(
            t("error.zip_too_large", lang, max_mb=MAX_OUTPUT_MB), parse_mode="HTML"
        )
        await _clear_state_and_tmp(state)
        return

    try:
        await status.edit_text(
            t("pdf.split.done", lang, count=len(files)), parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.message.answer_document(
        FSInputFile(zip_path, filename="pages.zip"),
    )
    await _finish_ok(callback, state, lang)


@router.callback_query(SplitStates.waiting_mode, F.data == "split:by_ranges")
async def split_by_ranges_prompt(
    callback: CallbackQuery, state: FSMContext
) -> None:
    lang = await _lang(callback.from_user.id)
    data = await state.get_data()
    await state.set_state(SplitStates.waiting_ranges)
    await callback.answer()
    await callback.message.edit_text(
        t("pdf.split.prompt_ranges", lang, pages=data["pages"]),
        reply_markup=get_cancel_only(lang),
        parse_mode="HTML",
    )


@router.message(SplitStates.waiting_ranges, F.text)
async def split_by_ranges_input(
    message: Message, state: FSMContext
) -> None:
    lang = await _lang(message.from_user.id)
    data = await state.get_data()
    pages: int = data["pages"]
    pdf_path = Path(data["pdf_path"])
    tmp_dir = Path(data["tmp_dir"])

    try:
        ranges = pdf_service.parse_ranges(message.text or "", pages)
    except InvalidRangeError as e:
        await message.answer(
            t("error.invalid_range", lang, details=str(e)),
            reply_markup=get_cancel_only(lang),
            parse_mode="HTML",
        )
        return

    status = await message.answer(
        t("pdf.split.processing", lang), parse_mode="HTML"
    )

    out_dir = tmp_dir / "split_ranges"
    out_dir.mkdir(exist_ok=True)
    try:
        files = await pdf_service.split_by_ranges(
            pdf_path, ranges, out_dir
        )
    except InvalidRangeError as e:
        await message.answer(
            t("error.invalid_range", lang, details=str(e)),
            reply_markup=get_cancel_only(lang),
            parse_mode="HTML",
        )
        return
    except Exception as e:
        await _handle_pdf_error(message, e, lang)
        await _clear_state_and_tmp(state)
        return

    zip_path = tmp_dir / "ranges.zip"
    await _zip_files(files, zip_path)

    if zip_path.stat().st_size >= MAX_UPLOAD_SIZE:
        try:
            await status.delete()
        except Exception:
            pass
        await message.answer(
            t("error.zip_too_large", lang, max_mb=MAX_OUTPUT_MB), parse_mode="HTML"
        )
        await _clear_state_and_tmp(state)
        return

    try:
        await status.edit_text(
            t("pdf.split.done", lang, count=len(files)), parse_mode="HTML"
        )
    except Exception:
        pass
    await message.answer_document(
        FSInputFile(zip_path, filename="ranges.zip"),
    )
    await _finish_ok(message, state, lang)


# === COMPRESS ===


@router.message(CompressStates.waiting_file, F.document)
async def compress_on_pdf(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id)
    data = await state.get_data()
    tmp_dir = Path(data["tmp_dir"])

    pdf_path = await _download_pdf(message, tmp_dir, lang)
    if not pdf_path:
        return

    await state.update_data(pdf_path=str(pdf_path))
    await state.set_state(CompressStates.waiting_level)
    await message.answer(
        t("pdf.compress.prompt_level", lang),
        reply_markup=get_compress_levels(lang),
        parse_mode="HTML",
    )


@router.callback_query(
    CompressStates.waiting_level, F.data.startswith("compress:")
)
async def compress_do(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(callback.from_user.id)
    level = callback.data.split(":", 1)[1]  # low / medium / high
    if level not in ("low", "medium", "high"):
        await callback.answer()
        return

    data = await state.get_data()
    pdf_path = Path(data["pdf_path"])
    tmp_dir = Path(data["tmp_dir"])
    output = tmp_dir / "compressed.pdf"

    await callback.answer()
    status = await callback.message.answer(
        t("pdf.compress.processing", lang), parse_mode="HTML"
    )

    try:
        await pdf_service.compress(pdf_path, output, level=level)
    except Exception as e:
        await _handle_pdf_error(callback.message, e, lang)
        await _clear_state_and_tmp(state)
        return

    before = pdf_path.stat().st_size
    after = output.stat().st_size
    percent = 0 if before == 0 else max(0, int(100 - after * 100 / before))

    try:
        await status.edit_text(
            t(
                "pdf.compress.done",
                lang,
                before=_human_mb(before),
                after=_human_mb(after),
                percent=percent,
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await callback.message.answer_document(
        FSInputFile(output, filename="compressed.pdf"),
    )
    await _finish_ok(callback, state, lang)


# === PASSWORD ===


@router.message(PasswordStates.waiting_file, F.document)
async def password_on_pdf(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id)
    data = await state.get_data()
    tmp_dir = Path(data["tmp_dir"])

    pdf_path = await _download_pdf(message, tmp_dir, lang)
    if not pdf_path:
        return

    await state.update_data(pdf_path=str(pdf_path))
    await state.set_state(PasswordStates.waiting_action)
    await message.answer(
        t("pdf.password.prompt_action", lang),
        reply_markup=get_password_actions(lang),
        parse_mode="HTML",
    )


@router.callback_query(PasswordStates.waiting_action, F.data == "password:set")
async def password_set_prompt(
    callback: CallbackQuery, state: FSMContext
) -> None:
    lang = await _lang(callback.from_user.id)
    await state.set_state(PasswordStates.waiting_password_set)
    await callback.answer()
    await callback.message.edit_text(
        t("pdf.password.prompt_set", lang),
        reply_markup=get_cancel_only(lang),
        parse_mode="HTML",
    )


@router.callback_query(
    PasswordStates.waiting_action, F.data == "password:remove"
)
async def password_remove_prompt(
    callback: CallbackQuery, state: FSMContext
) -> None:
    lang = await _lang(callback.from_user.id)
    data = await state.get_data()
    pdf_path = Path(data["pdf_path"])

    # если PDF не зашифрован — сразу сообщаем
    try:
        encrypted = await pdf_service.is_encrypted(pdf_path)
    except Exception as e:
        await _handle_pdf_error(callback.message, e, lang)
        await _clear_state_and_tmp(state)
        await callback.answer()
        return

    if not encrypted:
        await callback.answer()
        await callback.message.edit_text(
            t("pdf.password.not_encrypted", lang), parse_mode="HTML"
        )
        await _clear_state_and_tmp(state)
        return

    await state.set_state(PasswordStates.waiting_password_remove)
    await callback.answer()
    await callback.message.edit_text(
        t("pdf.password.prompt_remove", lang),
        reply_markup=get_cancel_only(lang),
        parse_mode="HTML",
    )


@router.message(PasswordStates.waiting_password_set, F.text)
async def password_set_do(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id)
    password = (message.text or "").strip()
    # удаляем сообщение с паролем из чата — чтобы не висело на виду
    try:
        await message.delete()
    except Exception:
        pass
    if not password:
        await message.answer(
            t("error.empty_password", lang),
            reply_markup=get_cancel_only(lang),
            parse_mode="HTML",
        )
        return

    data = await state.get_data()
    pdf_path = Path(data["pdf_path"])
    tmp_dir = Path(data["tmp_dir"])
    output = tmp_dir / "protected.pdf"

    status = await message.answer(
        t("status.processing", lang), parse_mode="HTML"
    )
    try:
        await pdf_service.set_password(pdf_path, output, password)
    except Exception as e:
        await _handle_pdf_error(message, e, lang)
        await _clear_state_and_tmp(state)
        return

    try:
        await status.edit_text(
            t("pdf.password.done_set", lang), parse_mode="HTML"
        )
    except Exception:
        pass
    await message.answer_document(
        FSInputFile(output, filename="protected.pdf"),
    )
    await _finish_ok(message, state, lang)


@router.message(PasswordStates.waiting_password_remove, F.text)
async def password_remove_do(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id)
    password = (message.text or "").strip()
    # удаляем сообщение с паролем из чата
    try:
        await message.delete()
    except Exception:
        pass
    if not password:
        await message.answer(
            t("error.empty_password", lang),
            reply_markup=get_cancel_only(lang),
            parse_mode="HTML",
        )
        return

    data = await state.get_data()
    pdf_path = Path(data["pdf_path"])
    tmp_dir = Path(data["tmp_dir"])
    output = tmp_dir / "unlocked.pdf"

    status = await message.answer(
        t("status.processing", lang), parse_mode="HTML"
    )
    try:
        await pdf_service.remove_password(pdf_path, output, password)
    except InvalidPassword:
        try:
            await status.delete()
        except Exception:
            pass
        await message.answer(
            t("error.invalid_password", lang),
            reply_markup=get_cancel_only(lang),
            parse_mode="HTML",
        )
        return
    except Exception as e:
        await _handle_pdf_error(message, e, lang)
        await _clear_state_and_tmp(state)
        return

    try:
        await status.edit_text(
            t("pdf.password.done_remove", lang), parse_mode="HTML"
        )
    except Exception:
        pass
    await message.answer_document(
        FSInputFile(output, filename="unlocked.pdf"),
    )
    await _finish_ok(message, state, lang)


# === PDF → Images ===


@router.message(PdfToImagesStates.waiting_file, F.document)
async def to_images_on_pdf(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id)
    data = await state.get_data()
    tmp_dir = Path(data["tmp_dir"])

    pdf_path = await _download_pdf(message, tmp_dir, lang)
    if not pdf_path:
        return

    try:
        pages = await pdf_service.get_page_count(pdf_path)
    except Exception as e:
        await _handle_pdf_error(message, e, lang)
        await _clear_state_and_tmp(state)
        return

    await state.update_data(pdf_path=str(pdf_path), pages=pages)

    if pages > LARGE_PDF_THRESHOLD:
        await state.set_state(PdfToImagesStates.waiting_confirm_large)
        await message.answer(
            t("pdf.to_images.confirm_large", lang, pages=pages),
            reply_markup=get_confirm_large(lang),
            parse_mode="HTML",
        )
    else:
        await state.set_state(PdfToImagesStates.waiting_quality)
        await message.answer(
            t("pdf.to_images.prompt_quality", lang),
            reply_markup=get_quality_levels(lang),
            parse_mode="HTML",
        )


@router.callback_query(
    PdfToImagesStates.waiting_confirm_large, F.data == "confirm_large:yes"
)
async def to_images_confirm_large(
    callback: CallbackQuery, state: FSMContext
) -> None:
    lang = await _lang(callback.from_user.id)
    await state.set_state(PdfToImagesStates.waiting_quality)
    await callback.answer()
    await callback.message.edit_text(
        t("pdf.to_images.prompt_quality", lang),
        reply_markup=get_quality_levels(lang),
        parse_mode="HTML",
    )


@router.callback_query(
    PdfToImagesStates.waiting_quality, F.data.startswith("dpi:")
)
async def to_images_do(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang(callback.from_user.id)
    try:
        dpi = int(callback.data.split(":", 1)[1])
    except ValueError:
        await callback.answer()
        return
    if dpi not in (150, 300, 600):
        await callback.answer()
        return

    data = await state.get_data()
    pdf_path = Path(data["pdf_path"])
    tmp_dir = Path(data["tmp_dir"])
    out_dir = tmp_dir / "images"
    out_dir.mkdir(exist_ok=True)

    await callback.answer()
    status = await callback.message.answer(
        t("pdf.to_images.processing", lang), parse_mode="HTML"
    )

    try:
        images = await pdf_service.pdf_to_images(pdf_path, out_dir, dpi=dpi)
    except Exception as e:
        await _handle_pdf_error(callback.message, e, lang)
        await _clear_state_and_tmp(state)
        return

    zip_path = tmp_dir / "images.zip"
    await _zip_files(images, zip_path)

    if zip_path.stat().st_size >= MAX_UPLOAD_SIZE:
        try:
            await status.delete()
        except Exception:
            pass
        await callback.message.answer(
            t("error.zip_too_large", lang, max_mb=MAX_OUTPUT_MB), parse_mode="HTML"
        )
        await _clear_state_and_tmp(state)
        return

    try:
        await status.edit_text(
            t("pdf.to_images.done", lang, count=len(images)),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await callback.message.answer_document(
        FSInputFile(zip_path, filename="images.zip"),
    )
    await _finish_ok(callback, state, lang)


# === Images → PDF ===


@router.message(
    ImagesToPdfStates.collecting_images, F.photo | F.document
)
async def images_collect(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id)
    data = await state.get_data()
    tmp_dir = Path(data["tmp_dir"])

    saved_path: Path | None = None

    if message.photo:
        photo = message.photo[-1]  # наибольший размер
        if photo.file_size and photo.file_size > MAX_FILE_SIZE:
            await message.answer(
                t("error.file_too_large", lang, max_mb=MAX_INPUT_MB), parse_mode="HTML"
            )
            return
        saved_path = tmp_dir / f"img_{photo.file_unique_id}.jpg"
        try:
            await _download_and_purge(message.bot, photo, saved_path)
        except Exception as e:
            logger.exception("Ошибка скачивания фото: %s", e)
            await message.answer(
                t("error.generic", lang), parse_mode="HTML"
            )
            return
    elif message.document:
        doc = message.document
        mime = (doc.mime_type or "").lower()
        if not mime.startswith("image/"):
            await message.answer(
                t("error.not_pdf", lang), parse_mode="HTML"
            )
            return
        if doc.file_size and doc.file_size > MAX_FILE_SIZE:
            await message.answer(
                t("error.file_too_large", lang, max_mb=MAX_INPUT_MB), parse_mode="HTML"
            )
            return
        suffix = Path(doc.file_name or "image").suffix or ".jpg"
        saved_path = tmp_dir / f"img_{doc.file_unique_id}{suffix}"
        try:
            await _download_and_purge(message.bot, doc, saved_path)
        except Exception as e:
            logger.exception("Ошибка скачивания изображения: %s", e)
            await message.answer(
                t("error.generic", lang), parse_mode="HTML"
            )
            return

    if saved_path is None:
        return

    images: list[str] = list(data.get("images", []))
    images.append(str(saved_path))
    await state.update_data(images=images)

    await message.answer(
        t("pdf.from_images.received", lang, count=len(images)),
        reply_markup=get_images_controls(lang, can_create=len(images) >= 1),
        parse_mode="HTML",
    )


@router.callback_query(
    ImagesToPdfStates.collecting_images, F.data == "images:add_more"
)
async def images_add_more(
    callback: CallbackQuery, state: FSMContext
) -> None:
    lang = await _lang(callback.from_user.id)
    await callback.answer()
    await callback.message.answer(
        t("pdf.from_images.prompt", lang), parse_mode="HTML"
    )


@router.callback_query(
    ImagesToPdfStates.collecting_images, F.data == "images:create"
)
async def images_create(
    callback: CallbackQuery, state: FSMContext
) -> None:
    lang = await _lang(callback.from_user.id)
    data = await state.get_data()
    images: list[str] = data.get("images", [])
    tmp_dir = Path(data["tmp_dir"])

    if not images:
        await callback.answer(t("error.need_min_1", lang), show_alert=True)
        return

    await callback.answer()
    status = await callback.message.answer(
        t("pdf.from_images.processing", lang), parse_mode="HTML"
    )

    output = tmp_dir / "images.pdf"
    try:
        await pdf_service.images_to_pdf(
            [Path(p) for p in images], output
        )
    except Exception as e:
        logger.exception("images_to_pdf error: %s", e)
        await callback.message.answer(
            t("error.generic", lang), parse_mode="HTML"
        )
        await _clear_state_and_tmp(state)
        return

    try:
        await status.edit_text(
            t("pdf.from_images.done", lang), parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.message.answer_document(
        FSInputFile(output, filename="images.pdf"),
    )
    await _finish_ok(callback, state, lang)


# === Extract text ===


@router.message(ExtractTextStates.waiting_file, F.document)
async def extract_on_pdf(message: Message, state: FSMContext) -> None:
    lang = await _lang(message.from_user.id)
    data = await state.get_data()
    tmp_dir = Path(data["tmp_dir"])

    pdf_path = await _download_pdf(message, tmp_dir, lang)
    if not pdf_path:
        return

    status = await message.answer(
        t("pdf.extract.processing", lang), parse_mode="HTML"
    )
    try:
        text = await pdf_service.extract_text(pdf_path)
    except Exception as e:
        await _handle_pdf_error(message, e, lang)
        await _clear_state_and_tmp(state)
        return

    if not text or not text.strip():
        try:
            await status.delete()
        except Exception:
            pass
        await message.answer(
            t("error.scan_no_text", lang), parse_mode="HTML"
        )
        await _clear_state_and_tmp(state)
        return

    try:
        await status.edit_text(
            t("pdf.extract.done", lang, chars=len(text)), parse_mode="HTML"
        )
    except Exception:
        pass

    # отдаём .txt как document через BufferedInputFile (не пишем на диск лишний раз)
    data_bytes = text.encode("utf-8")
    if len(data_bytes) >= MAX_UPLOAD_SIZE:
        await message.answer(
            t("error.text_too_large", lang, max_mb=MAX_OUTPUT_MB), parse_mode="HTML"
        )
        await _clear_state_and_tmp(state)
        return
    await message.answer_document(
        BufferedInputFile(data_bytes, filename="extracted.txt"),
    )
    await _finish_ok(message, state, lang)


# === Утилита: ZIP ===


async def _zip_files(files: list[Path], zip_path: Path) -> None:
    """Упаковывает файлы в ZIP (в to_thread, т.к. I/O)."""

    def _sync_zip() -> None:
        with zipfile.ZipFile(
            zip_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            for f in files:
                zf.write(f, arcname=f.name)

    await asyncio.to_thread(_sync_zip)
