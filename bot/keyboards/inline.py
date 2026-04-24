"""Inline-клавиатуры — меню, подписка, PDF операции"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import settings
from bot.emojis import E_ID
from bot.i18n import t


def get_start_keyboard(user_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Главное меню бота"""
    buttons = [
        [InlineKeyboardButton(
            text=t("btn.pdf_tools", lang),
            callback_data="pdf_menu",
            style="primary",
            icon_custom_emoji_id=E_ID["folder"],
        )],
        [
            InlineKeyboardButton(
                text=t("btn.profile", lang),
                callback_data="my_profile",
                style="success",
                icon_custom_emoji_id=E_ID["profile"],
            ),
            InlineKeyboardButton(
                text=t("btn.help", lang),
                callback_data="help",
                style="success",
                icon_custom_emoji_id=E_ID["info"],
            ),
        ],
        [InlineKeyboardButton(
            text=t("btn.language", lang),
            callback_data="change_language",
            style="success",
            icon_custom_emoji_id=E_ID["gear"],
        )],
    ]

    # кнопка админки для админов
    if user_id in settings.admin_id_list:
        buttons.append([InlineKeyboardButton(
            text=t("btn.admin_panel", lang),
            callback_data="admin_panel",
            style="danger",
            icon_custom_emoji_id=E_ID["lock"],
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка 'Назад' в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_pdf_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню PDF инструментов — 7 операций"""
    buttons = [
        [InlineKeyboardButton(
            text=t("btn.merge", lang),
            callback_data="pdf:merge",
            style="primary",
            icon_custom_emoji_id=E_ID["plus"],
        )],
        [InlineKeyboardButton(
            text=t("btn.split", lang),
            callback_data="pdf:split",
            style="primary",
            icon_custom_emoji_id=E_ID["edit"],
        )],
        [InlineKeyboardButton(
            text=t("btn.compress", lang),
            callback_data="pdf:compress",
            style="primary",
            icon_custom_emoji_id=E_ID["package"],
        )],
        [InlineKeyboardButton(
            text=t("btn.password", lang),
            callback_data="pdf:password",
            style="primary",
            icon_custom_emoji_id=E_ID["lock"],
        )],
        [
            InlineKeyboardButton(
                text=t("btn.pdf_to_images", lang),
                callback_data="pdf:to_images",
                style="primary",
                icon_custom_emoji_id=E_ID["camera"],
            ),
            InlineKeyboardButton(
                text=t("btn.images_to_pdf", lang),
                callback_data="pdf:from_images",
                style="primary",
                icon_custom_emoji_id=E_ID["folder"],
            ),
        ],
        [InlineKeyboardButton(
            text=t("btn.extract_text", lang),
            callback_data="pdf:extract",
            style="primary",
            icon_custom_emoji_id=E_ID["book"],
        )],
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_only(lang: str = "ru") -> InlineKeyboardMarkup:
    """Только кнопка «Отмена» — для FSM-шагов ввода."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=t("btn.cancel", lang),
            callback_data="cancel_op",
            style="danger",
            icon_custom_emoji_id=E_ID["cross"],
        ),
    ]])


def get_merge_controls(lang: str = "ru", can_merge: bool = False) -> InlineKeyboardMarkup:
    """Кнопки в процессе сбора PDF для merge."""
    rows: list[list[InlineKeyboardButton]] = []
    if can_merge:
        rows.append([InlineKeyboardButton(
            text=t("btn.do_merge", lang),
            callback_data="merge:do",
            style="success",
            icon_custom_emoji_id=E_ID["check"],
        )])
    rows.append([InlineKeyboardButton(
        text=t("btn.add_more", lang),
        callback_data="merge:add_more",
        style="primary",
        icon_custom_emoji_id=E_ID["plus"],
    )])
    rows.append([InlineKeyboardButton(
        text=t("btn.cancel", lang),
        callback_data="cancel_op",
        style="danger",
        icon_custom_emoji_id=E_ID["cross"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_split_mode(lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор режима split."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.per_page", lang),
            callback_data="split:per_page",
            style="primary",
            icon_custom_emoji_id=E_ID["edit"],
        )],
        [InlineKeyboardButton(
            text=t("btn.by_ranges", lang),
            callback_data="split:by_ranges",
            style="primary",
            icon_custom_emoji_id=E_ID["edit"],
        )],
        [InlineKeyboardButton(
            text=t("btn.cancel", lang),
            callback_data="cancel_op",
            style="danger",
            icon_custom_emoji_id=E_ID["cross"],
        )],
    ])


def get_compress_levels(lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор уровня сжатия."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.compress_low", lang),
            callback_data="compress:low",
            style="primary",
        )],
        [InlineKeyboardButton(
            text=t("btn.compress_medium", lang),
            callback_data="compress:medium",
            style="primary",
        )],
        [InlineKeyboardButton(
            text=t("btn.compress_high", lang),
            callback_data="compress:high",
            style="primary",
        )],
        [InlineKeyboardButton(
            text=t("btn.cancel", lang),
            callback_data="cancel_op",
            style="danger",
            icon_custom_emoji_id=E_ID["cross"],
        )],
    ])


def get_password_actions(lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор действия с паролем."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.set_password", lang),
            callback_data="password:set",
            style="primary",
            icon_custom_emoji_id=E_ID["lock"],
        )],
        [InlineKeyboardButton(
            text=t("btn.remove_password", lang),
            callback_data="password:remove",
            style="primary",
            icon_custom_emoji_id=E_ID["lock"],
        )],
        [InlineKeyboardButton(
            text=t("btn.cancel", lang),
            callback_data="cancel_op",
            style="danger",
            icon_custom_emoji_id=E_ID["cross"],
        )],
    ])


def get_quality_levels(lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор DPI для PDF→Images."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=t("btn.dpi_150", lang),
                callback_data="dpi:150",
                style="primary",
            ),
            InlineKeyboardButton(
                text=t("btn.dpi_300", lang),
                callback_data="dpi:300",
                style="primary",
            ),
            InlineKeyboardButton(
                text=t("btn.dpi_600", lang),
                callback_data="dpi:600",
                style="primary",
            ),
        ],
        [InlineKeyboardButton(
            text=t("btn.cancel", lang),
            callback_data="cancel_op",
            style="danger",
            icon_custom_emoji_id=E_ID["cross"],
        )],
    ])


def get_confirm_large(lang: str = "ru") -> InlineKeyboardMarkup:
    """Подтверждение обработки большого PDF."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.continue", lang),
            callback_data="confirm_large:yes",
            style="success",
            icon_custom_emoji_id=E_ID["check"],
        )],
        [InlineKeyboardButton(
            text=t("btn.cancel", lang),
            callback_data="cancel_op",
            style="danger",
            icon_custom_emoji_id=E_ID["cross"],
        )],
    ])


def get_images_controls(lang: str = "ru", can_create: bool = False) -> InlineKeyboardMarkup:
    """Кнопки в процессе сбора изображений для images_to_pdf."""
    rows: list[list[InlineKeyboardButton]] = []
    if can_create:
        rows.append([InlineKeyboardButton(
            text=t("btn.create_pdf", lang),
            callback_data="images:create",
            style="success",
            icon_custom_emoji_id=E_ID["check"],
        )])
    rows.append([InlineKeyboardButton(
        text=t("btn.add_more", lang),
        callback_data="images:add_more",
        style="primary",
        icon_custom_emoji_id=E_ID["plus"],
    )])
    rows.append([InlineKeyboardButton(
        text=t("btn.cancel", lang),
        callback_data="cancel_op",
        style="danger",
        icon_custom_emoji_id=E_ID["cross"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_subscription_keyboard(
    channels: list[dict], lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Клавиатура подписки на каналы"""
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(
            text=f"{ch['title']}",
            url=ch["invite_link"],
            style="primary",
            icon_custom_emoji_id=E_ID["megaphone"],
        )])
    buttons.append([InlineKeyboardButton(
        text=t("btn.check_sub", lang),
        callback_data="check_subscription",
        style="success",
        icon_custom_emoji_id=E_ID["check"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Русский",
                callback_data="set_lang_ru",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_ru"],
            ),
            InlineKeyboardButton(
                text="O'zbek",
                callback_data="set_lang_uz",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_uz"],
            ),
            InlineKeyboardButton(
                text="English",
                callback_data="set_lang_en",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_gb"],
            ),
        ],
    ])
