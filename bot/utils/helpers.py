"""Вспомогательные утилиты для PDF-бота"""

# максимальный размер файла для обработки (20 МБ)
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024


def is_pdf_file(mime_type: str | None, file_name: str | None) -> bool:
    """Проверяет, является ли файл PDF"""
    if mime_type == "application/pdf":
        return True
    if file_name and file_name.lower().endswith(".pdf"):
        return True
    return False


def is_image_file(mime_type: str | None, file_name: str | None) -> bool:
    """Проверяет, является ли файл изображением"""
    image_mimes = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/bmp"}
    image_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

    if mime_type in image_mimes:
        return True
    if file_name:
        ext = "." + file_name.lower().rsplit(".", 1)[-1] if "." in file_name else ""
        if ext in image_exts:
            return True
    return False


def file_size_ok(file_size: int | None) -> bool:
    """Проверяет, не превышает ли файл лимит"""
    if file_size is None:
        return True
    return file_size <= MAX_FILE_SIZE_BYTES


def format_file_size(size_bytes: int) -> str:
    """Форматирует размер файла в человекочитаемый вид"""
    if size_bytes < 1024:
        return f"{size_bytes} Б"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} КБ"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} МБ"
