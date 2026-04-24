"""Мультиязычность — русский, узбекский, английский
Использование: from bot.i18n import t
  t("start.welcome", lang="en", name="John")
"""

from bot.emojis import E

TRANSLATIONS = {
    # === /start ===
    "start.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет, {{name}}!</b>\n\n"
            f"{E['folder']} Я помогу тебе работать с PDF-файлами.\n\n"
            f"{E['pin']} <b>Что умею:</b>\n"
            "Объединять, разделять, сжимать PDF, "
            "конвертировать в изображения и обратно, "
            f"извлекать текст и защищать паролем! {E['lock']}\n\n"
            "Выбери действие ниже:"
        ),
        "uz": (
            f"{E['bot']} <b>Salom, {{name}}!</b>\n\n"
            f"{E['folder']} Men senga PDF fayllar bilan ishlashda yordam beraman.\n\n"
            f"{E['pin']} <b>Nima qila olaman:</b>\n"
            "PDF birlashtirish, bo'lish, siqish, "
            "rasmlarga va aksincha aylantirish, "
            f"matn ajratish va parol bilan himoya qilish! {E['lock']}\n\n"
            "Quyidagi amallardan birini tanla:"
        ),
        "en": (
            f"{E['bot']} <b>Hello, {{name}}!</b>\n\n"
            f"{E['folder']} I'll help you work with PDF files.\n\n"
            f"{E['pin']} <b>What I can do:</b>\n"
            "Merge, split, compress PDFs, "
            "convert to images and back, "
            f"extract text and protect with password! {E['lock']}\n\n"
            "Choose an action below:"
        ),
    },

    # === Кнопки главного меню ===
    "btn.pdf_tools": {
        "ru": "PDF инструменты",
        "uz": "PDF vositalari",
        "en": "PDF tools",
    },
    "btn.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "btn.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "btn.back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },

    # === PDF операции (кнопки) ===
    "btn.merge": {
        "ru": "Объединить PDF",
        "uz": "PDF birlashtirish",
        "en": "Merge PDF",
    },
    "btn.split": {
        "ru": "Разделить PDF",
        "uz": "PDF bo'lish",
        "en": "Split PDF",
    },
    "btn.compress": {
        "ru": "Сжать PDF",
        "uz": "PDF siqish",
        "en": "Compress PDF",
    },
    "btn.password": {
        "ru": "Защита паролем",
        "uz": "Parol himoyasi",
        "en": "Password protect",
    },
    "btn.pdf_to_images": {
        "ru": "PDF → Картинки",
        "uz": "PDF → Rasmlar",
        "en": "PDF → Images",
    },
    "btn.images_to_pdf": {
        "ru": "Картинки → PDF",
        "uz": "Rasmlar → PDF",
        "en": "Images → PDF",
    },
    "btn.extract_text": {
        "ru": "Извлечь текст",
        "uz": "Matn ajratish",
        "en": "Extract text",
    },

    # === PDF меню ===
    "pdf.menu": {
        "ru": (
            f"{E['folder']} <b>PDF инструменты</b>\n\n"
            "Выбери операцию:"
        ),
        "uz": (
            f"{E['folder']} <b>PDF vositalari</b>\n\n"
            "Amalni tanla:"
        ),
        "en": (
            f"{E['folder']} <b>PDF tools</b>\n\n"
            "Choose an operation:"
        ),
    },

    # === Профиль ===
    "profile.title": {
        "ru": (
            f"{E['profile']} <b>Твой профиль</b>\n\n"
            f"{E['edit']} Имя: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Обработок (всего): {{downloads}}\n"
        ),
        "uz": (
            f"{E['profile']} <b>Sening profilin</b>\n\n"
            f"{E['edit']} Ism: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Ishlovlar (jami): {{downloads}}\n"
        ),
        "en": (
            f"{E['profile']} <b>Your profile</b>\n\n"
            f"{E['edit']} Name: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Processed (total): {{downloads}}\n"
        ),
    },

    # === Помощь ===
    "help.text": {
        "ru": (
            f"{E['book']} <b>Помощь</b>\n\n"
            f"{E['star']} Отправь PDF файл и выбери операцию\n"
            f"{E['star']} Поддерживаются: объединение, разделение, сжатие\n"
            f"{E['star']} Конвертация PDF ↔ изображения\n"
            f"{E['star']} Извлечение текста и защита паролем\n"
            f"{E['lock']} Максимальный размер файла: {{max_mb}} МБ\n\n"
            f"{E['plane']} По вопросам: @{{admin_username}}"
        ),
        "uz": (
            f"{E['book']} <b>Yordam</b>\n\n"
            f"{E['star']} PDF faylni yubor va amalni tanla\n"
            f"{E['star']} Qo'llab-quvvatlanadi: birlashtirish, bo'lish, siqish\n"
            f"{E['star']} PDF ↔ rasmlar konvertatsiyasi\n"
            f"{E['star']} Matn ajratish va parol himoyasi\n"
            f"{E['lock']} Maksimal fayl hajmi: {{max_mb}} MB\n\n"
            f"{E['plane']} Savollar uchun: @{{admin_username}}"
        ),
        "en": (
            f"{E['book']} <b>Help</b>\n\n"
            f"{E['star']} Send a PDF file and choose an operation\n"
            f"{E['star']} Supported: merge, split, compress\n"
            f"{E['star']} PDF ↔ images conversion\n"
            f"{E['star']} Text extraction and password protection\n"
            f"{E['lock']} Maximum file size: {{max_mb}} MB\n\n"
            f"{E['plane']} Contact: @{{admin_username}}"
        ),
    },

    # === Подписка ===
    "sub.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет!</b>\n\n"
            f"{E['folder']} Этот бот помогает работать с PDF — "
            "быстро и бесплатно!\n\n"
            f"{E['lock']} <b>Для начала подпишись на каналы ниже:</b>\n\n"
            f"После подписки нажми «{E['check']} Проверить подписку»"
        ),
        "uz": (
            f"{E['bot']} <b>Salom!</b>\n\n"
            f"{E['folder']} Bu bot PDF fayllar bilan ishlashga yordam beradi — "
            "tez va bepul!\n\n"
            f"{E['lock']} <b>Boshlash uchun quyidagi kanallarga obuna bo'l:</b>\n\n"
            f"Obuna bo'lgandan so'ng «{E['check']} Obunani tekshirish» tugmasini bos"
        ),
        "en": (
            f"{E['bot']} <b>Hello!</b>\n\n"
            f"{E['folder']} This bot helps you work with PDF files — "
            "fast and free!\n\n"
            f"{E['lock']} <b>To start, subscribe to the channels below:</b>\n\n"
            f"After subscribing, tap «{E['check']} Check subscription»"
        ),
    },
    "sub.not_subscribed": {
        "ru": (
            f"{E['cross']} <b>Ты ещё не подписался на все каналы:</b>\n\n"
            f"Подпишись и нажми «{E['check']} Проверить подписку» ещё раз."
        ),
        "uz": (
            f"{E['cross']} <b>Sen hali barcha kanallarga obuna bo'lmading:</b>\n\n"
            f"Obuna bo'l va «{E['check']} Obunani tekshirish» tugmasini qayta bos."
        ),
        "en": (
            f"{E['cross']} <b>You haven't subscribed to all channels yet:</b>\n\n"
            f"Subscribe and tap «{E['check']} Check subscription» again."
        ),
    },
    "sub.success": {
        "ru": (
            f"{E['check']} <b>Отлично, {{name}}!</b>\n\n"
            f"Теперь ты можешь пользоваться ботом! {E['plane']}\n\n"
            "Отправь PDF файл или выбери операцию."
        ),
        "uz": (
            f"{E['check']} <b>Ajoyib, {{name}}!</b>\n\n"
            f"Endi botdan foydalanishing mumkin! {E['plane']}\n\n"
            "PDF faylini yubor yoki amalni tanla."
        ),
        "en": (
            f"{E['check']} <b>Great, {{name}}!</b>\n\n"
            f"You can now use the bot! {E['plane']}\n\n"
            "Send a PDF file or choose an operation."
        ),
    },
    "btn.check_sub": {
        "ru": "Проверить подписку",
        "uz": "Obunani tekshirish",
        "en": "Check subscription",
    },
    "sub.check_alert_fail": {
        "ru": f"{E['cross']} Подпишись на все каналы!",
        "uz": f"{E['cross']} Barcha kanallarga obuna bo'l!",
        "en": f"{E['cross']} Subscribe to all channels!",
    },
    "sub.check_alert_ok": {
        "ru": f"{E['check']} Подписка подтверждена!",
        "uz": f"{E['check']} Obuna tasdiqlandi!",
        "en": f"{E['check']} Subscription confirmed!",
    },
    "sub.not_required": {
        "ru": f"{E['check']} Подписка не требуется!",
        "uz": f"{E['check']} Obuna talab qilinmaydi!",
        "en": f"{E['check']} No subscription required!",
    },

    # === Ошибки ===
    "error.rate_limit": {
        "ru": f"{E['clock']} <b>Слишком много запросов!</b>\n\nПодожди {{seconds}} секунд и попробуй снова.",
        "uz": f"{E['clock']} <b>Juda ko'p so'rovlar!</b>\n\n{{seconds}} soniya kut va qayta urinib ko'r.",
        "en": f"{E['clock']} <b>Too many requests!</b>\n\nWait {{seconds}} seconds and try again.",
    },
    "error.generic": {
        "ru": f"{E['cross']} <b>Ошибка обработки</b>\n\nПопробуй позже.",
        "uz": f"{E['cross']} <b>Ishlov berish xatosi</b>\n\nKeyinroq urinib ko'r.",
        "en": f"{E['cross']} <b>Processing error</b>\n\nTry again later.",
    },
    "error.file_too_large": {
        "ru": f"{E['package']} <b>Файл слишком большой</b>\n\nПришли файл меньше {{max_mb}} МБ.",
        "uz": f"{E['package']} <b>Fayl juda katta</b>\n\n{{max_mb}} MB dan kichik fayl yubor.",
        "en": f"{E['package']} <b>File too large</b>\n\nPlease send a file smaller than {{max_mb}} MB.",
    },
    "error.not_pdf": {
        "ru": f"{E['cross']} <b>Неверный формат</b>\n\nПришли PDF файл.",
        "uz": f"{E['cross']} <b>Noto'g'ri format</b>\n\nPDF fayl yubor.",
        "en": f"{E['cross']} <b>Wrong format</b>\n\nPlease send a PDF file.",
    },
    "error.zip_too_large": {
        "ru": f"{E['package']} <b>Архив слишком большой</b>\n\nРезультат превышает {{max_mb}} МБ — Telegram не сможет его отправить. Попробуй меньший PDF или меньший DPI.",
        "uz": f"{E['package']} <b>Arxiv juda katta</b>\n\nNatija {{max_mb}} MB dan oshdi — Telegram uni yubora olmaydi. Kichikroq PDF yoki DPI tanla.",
        "en": f"{E['package']} <b>Archive too large</b>\n\nResult exceeds {{max_mb}} MB — Telegram cannot send it. Try a smaller PDF or lower DPI.",
    },
    "error.text_too_large": {
        "ru": f"{E['package']} <b>Текст слишком большой</b>\n\nИзвлечённый текст превышает {{max_mb}} МБ — Telegram не сможет его отправить.",
        "uz": f"{E['package']} <b>Matn juda katta</b>\n\nAjratib olingan matn {{max_mb}} MB dan oshdi — Telegram uni yubora olmaydi.",
        "en": f"{E['package']} <b>Text too large</b>\n\nExtracted text exceeds {{max_mb}} MB — Telegram cannot send it.",
    },
    "error.empty_password": {
        "ru": f"{E['cross']} <b>Пустой пароль</b>\n\nВведи непустой пароль.",
        "uz": f"{E['cross']} <b>Bo'sh parol</b>\n\nBo'sh bo'lmagan parol kirit.",
        "en": f"{E['cross']} <b>Empty password</b>\n\nPlease enter a non-empty password.",
    },

    # === Выбор языка ===
    "lang.choose": {
        "ru": f"{E['gear']} <b>Выберите язык:</b>",
        "uz": f"{E['gear']} <b>Tilni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose language:</b>",
    },
    "lang.changed": {
        "ru": f"{E['check']} Язык изменён на русский",
        "uz": f"{E['check']} Til o'zbek tiliga o'zgartirildi",
        "en": f"{E['check']} Language changed to English",
    },

    # === Админ-панель ===
    "admin.title": {
        "ru": f"{E['gear']} <b>Админ-панель</b>\n\nВыбери действие:",
        "uz": f"{E['gear']} <b>Admin panel</b>\n\nAmalni tanlang:",
        "en": f"{E['gear']} <b>Admin panel</b>\n\nChoose an action:",
    },
    "admin.no_access": {
        "ru": f"{E['lock']} У тебя нет доступа к админке.",
        "uz": f"{E['lock']} Sizda admin panelga kirish huquqi yo'q.",
        "en": f"{E['lock']} You don't have access to admin panel.",
    },
    "admin.stats": {
        "ru": (
            f"{E['chart']} <b>Статистика бота</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых юзеров сегодня: <b>{{today_users}}</b>\n"
            f"{E['download']} Всего обработок: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Bot statistikasi</b>\n\n"
            f"{E['users']} Jami foydalanuvchilar: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugungi yangi foydalanuvchilar: <b>{{today_users}}</b>\n"
            f"{E['download']} Jami ishlovlar: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Bot statistics</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New users today: <b>{{today_users}}</b>\n"
            f"{E['download']} Total processed: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },
    "admin.channels_empty": {
        "ru": f"{E['megaphone']} <b>Каналы</b>\n\nСписок пуст. Добавь канал кнопкой ниже.",
        "uz": f"{E['megaphone']} <b>Kanallar</b>\n\nRo'yxat bo'sh. Quyidagi tugma orqali kanal qo'shing.",
        "en": f"{E['megaphone']} <b>Channels</b>\n\nList is empty. Add a channel using the button below.",
    },
    "admin.channels_title": {
        "ru": f"{E['megaphone']} <b>Каналы для подписки:</b>\n",
        "uz": f"{E['megaphone']} <b>Obuna kanallari:</b>\n",
        "en": f"{E['megaphone']} <b>Subscription channels:</b>\n",
    },
    "admin.add_channel_id": {
        "ru": (
            f"{E['megaphone']} <b>Добавление канала</b>\n\n"
            "Отправь <b>ID канала</b> (например <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Узнать ID: добавь бота @getmyid_bot в канал"
        ),
        "uz": (
            f"{E['megaphone']} <b>Kanal qo'shish</b>\n\n"
            "<b>Kanal ID</b> raqamini yuboring (masalan <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} ID bilish: @getmyid_bot ni kanalga qo'shing"
        ),
        "en": (
            f"{E['megaphone']} <b>Add channel</b>\n\n"
            "Send the <b>channel ID</b> (e.g. <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Get ID: add @getmyid_bot to the channel"
        ),
    },
    "admin.add_channel_title": {
        "ru": f"{E['edit']} Теперь отправь <b>название канала</b>:",
        "uz": f"{E['edit']} Endi <b>kanal nomini</b> yuboring:",
        "en": f"{E['edit']} Now send the <b>channel name</b>:",
    },
    "admin.add_channel_link": {
        "ru": (
            f"{E['link']} Теперь отправь <b>ссылку или юзернейм канала</b>\n\n"
            "Принимаю любой формат:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "uz": (
            f"{E['link']} Endi <b>kanal havolasi yoki username</b> yuboring\n\n"
            "Istalgan formatda:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "en": (
            f"{E['link']} Now send the <b>channel link or username</b>\n\n"
            "Any format accepted:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
    },
    "admin.channel_added": {
        "ru": f"{E['check']} <b>Канал добавлен!</b>",
        "uz": f"{E['check']} <b>Kanal qo'shildi!</b>",
        "en": f"{E['check']} <b>Channel added!</b>",
    },
    "admin.confirm_delete": {
        "ru": f"{E['warning']} <b>Удалить канал?</b>\n\nID: <code>{{channel_id}}</code>\n\nЭто действие нельзя отменить.",
        "uz": f"{E['warning']} <b>Kanalni o'chirishni xohlaysizmi?</b>\n\nID: <code>{{channel_id}}</code>\n\nBu amalni qaytarib bo'lmaydi.",
        "en": f"{E['warning']} <b>Delete channel?</b>\n\nID: <code>{{channel_id}}</code>\n\nThis action cannot be undone.",
    },
    "admin.id_not_number": {
        "ru": f"{E['cross']} ID должен быть числом. Попробуй ещё раз:",
        "uz": f"{E['cross']} ID raqam bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} ID must be a number. Try again:",
    },
    "admin.title_too_long": {
        "ru": f"{E['cross']} Название слишком длинное (макс 200 символов)",
        "uz": f"{E['cross']} Nom juda uzun (maks 200 belgi)",
        "en": f"{E['cross']} Name is too long (max 200 characters)",
    },
    "admin.link_invalid": {
        "ru": f"{E['cross']} Не удалось распознать ссылку.\nПопробуй ещё:",
        "uz": f"{E['cross']} Havolani aniqlab bo'lmadi.\nQayta urinib ko'ring:",
        "en": f"{E['cross']} Could not parse the link.\nTry again:",
    },

    # === Кнопки админки ===
    "btn.admin_stats": {"ru": "Статистика", "uz": "Statistika", "en": "Statistics"},
    "btn.admin_channels": {"ru": "Каналы", "uz": "Kanallar", "en": "Channels"},
    "btn.admin_home": {"ru": "Главное меню", "uz": "Bosh menyu", "en": "Main menu"},
    "btn.admin_add": {"ru": "Добавить канал", "uz": "Kanal qo'shish", "en": "Add channel"},
    "btn.admin_back": {"ru": "Назад", "uz": "Orqaga", "en": "Back"},
    "btn.admin_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_confirm_del": {"ru": "Да, удалить", "uz": "Ha, o'chirish", "en": "Yes, delete"},
    "btn.admin_cancel_del": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_panel": {"ru": "Админ-панель", "uz": "Admin panel", "en": "Admin panel"},
    "btn.admin_broadcast": {"ru": "Рассылка", "uz": "Xabar tarqatish", "en": "Broadcast"},

    # === Рассылка ===
    "admin.broadcast_prompt": {
        "ru": f"{E['plane']} <b>Массовая рассылка</b>\n\nОтправь текст/фото/видео для рассылки.\nПоддерживается HTML.",
        "uz": f"{E['plane']} <b>Ommaviy xabar</b>\n\nYuborish uchun matn/rasm/video yuboring.\nHTML qo'llab-quvvatlanadi.",
        "en": f"{E['plane']} <b>Mass broadcast</b>\n\nSend text/photo/video to broadcast.\nHTML supported.",
    },
    "admin.broadcast_preview": {
        "ru": f"{E['eye']} <b>Предпросмотр</b>\n\nОтправить это сообщение всем юзерам?",
        "uz": f"{E['eye']} <b>Oldindan ko'rish</b>\n\nBu xabarni barcha foydalanuvchilarga yuborishni xohlaysizmi?",
        "en": f"{E['eye']} <b>Preview</b>\n\nSend this message to all users?",
    },
    "admin.broadcast_confirm": {"ru": "Да, отправить", "uz": "Ha, yuborish", "en": "Yes, send"},
    "admin.broadcast_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "admin.broadcast_started": {
        "ru": f"{E['plane']} Рассылка запущена... Ожидай отчёт.",
        "uz": f"{E['plane']} Xabar yuborilmoqda... Hisobotni kuting.",
        "en": f"{E['plane']} Broadcast started... Wait for report.",
    },
    "admin.broadcast_done": {
        "ru": f"{E['chart']} <b>Рассылка завершена!</b>\n\n{E['check']} Доставлено: <b>{{success}}</b>\n{E['cross']} Ошибок: <b>{{failed}}</b>\n{E['users']} Всего: <b>{{total}}</b>",
        "uz": f"{E['chart']} <b>Xabar yuborish tugadi!</b>\n\n{E['check']} Yetkazildi: <b>{{success}}</b>\n{E['cross']} Xatolar: <b>{{failed}}</b>\n{E['users']} Jami: <b>{{total}}</b>",
        "en": f"{E['chart']} <b>Broadcast complete!</b>\n\n{E['check']} Delivered: <b>{{success}}</b>\n{E['cross']} Failed: <b>{{failed}}</b>\n{E['users']} Total: <b>{{total}}</b>",
    },

    # === Описания команд бота (для меню Telegram) ===
    "cmd.start": {
        "ru": "Запустить бота",
        "uz": "Botni boshlash",
        "en": "Start the bot",
    },
    "cmd.menu": {
        "ru": "Главное меню",
        "uz": "Bosh menyu",
        "en": "Main menu",
    },
    "cmd.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "cmd.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "cmd.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
    "cmd.cancel": {
        "ru": "Отменить действие",
        "uz": "Amalni bekor qilish",
        "en": "Cancel action",
    },

    # === PDF: общие статусы ===
    "status.downloading": {
        "ru": f"{E['download']} Загружаю файл...",
        "uz": f"{E['download']} Fayl yuklanmoqda...",
        "en": f"{E['download']} Downloading file...",
    },
    "status.processing": {
        "ru": f"{E['gear']} Обрабатываю...",
        "uz": f"{E['gear']} Qayta ishlanmoqda...",
        "en": f"{E['gear']} Processing...",
    },
    "status.sending": {
        "ru": f"{E['plane']} Отправляю результат...",
        "uz": f"{E['plane']} Natija yuborilmoqda...",
        "en": f"{E['plane']} Sending result...",
    },

    # === PDF: ошибки ===
    "error.pdf_read_failed": {
        "ru": f"{E['cross']} <b>Не удалось прочитать PDF</b>\n\nФайл повреждён или имеет нестандартную структуру.",
        "uz": f"{E['cross']} <b>PDF o'qib bo'lmadi</b>\n\nFayl buzilgan yoki nostandart tuzilishga ega.",
        "en": f"{E['cross']} <b>Failed to read PDF</b>\n\nFile is corrupted or has a non-standard structure.",
    },
    "error.pdf_encrypted": {
        "ru": f"{E['lock']} <b>PDF защищён паролем</b>\n\nСначала сними защиту в разделе «Защита паролем».",
        "uz": f"{E['lock']} <b>PDF parol bilan himoyalangan</b>\n\nAvval «Parol himoyasi» bo'limida parolni olib tashlang.",
        "en": f"{E['lock']} <b>PDF is password-protected</b>\n\nRemove the password first in the «Password protect» section.",
    },
    "error.invalid_password": {
        "ru": f"{E['cross']} <b>Неверный пароль</b>\n\nПопробуй ещё раз или /cancel для отмены.",
        "uz": f"{E['cross']} <b>Noto'g'ri parol</b>\n\nQayta urinib ko'ring yoki /cancel — bekor qilish.",
        "en": f"{E['cross']} <b>Wrong password</b>\n\nTry again or /cancel to abort.",
    },
    "error.invalid_range": {
        "ru": (
            f"{E['cross']} <b>Неверный диапазон страниц</b>\n\n"
            "Формат: <code>1-5, 7, 10-12</code>\n"
            f"{{details}}\n\n"
            "Попробуй ещё раз:"
        ),
        "uz": (
            f"{E['cross']} <b>Noto'g'ri sahifa diapazoni</b>\n\n"
            "Format: <code>1-5, 7, 10-12</code>\n"
            f"{{details}}\n\n"
            "Qayta urinib ko'ring:"
        ),
        "en": (
            f"{E['cross']} <b>Invalid page range</b>\n\n"
            "Format: <code>1-5, 7, 10-12</code>\n"
            f"{{details}}\n\n"
            "Try again:"
        ),
    },
    "error.scan_no_text": {
        "ru": f"{E['warning']} <b>В PDF нет текста</b>\n\nСкорее всего это скан. Попробуй OCR-сервис.",
        "uz": f"{E['warning']} <b>PDF-da matn yo'q</b>\n\nEhtimol bu skanerlangan hujjat. OCR xizmatidan foydalaning.",
        "en": f"{E['warning']} <b>No text in PDF</b>\n\nThis is likely a scanned document. Try an OCR service.",
    },
    "error.need_min_2": {
        "ru": f"{E['warning']} Нужно минимум <b>2 файла</b> для объединения.",
        "uz": f"{E['warning']} Birlashtirish uchun kamida <b>2 ta fayl</b> kerak.",
        "en": f"{E['warning']} You need at least <b>2 files</b> to merge.",
    },
    "error.need_min_1": {
        "ru": f"{E['warning']} Нужно минимум <b>1 изображение</b>.",
        "uz": f"{E['warning']} Kamida <b>1 ta rasm</b> kerak.",
        "en": f"{E['warning']} You need at least <b>1 image</b>.",
    },
    "error.operation_cancelled": {
        "ru": f"{E['cross']} Операция отменена.",
        "uz": f"{E['cross']} Amal bekor qilindi.",
        "en": f"{E['cross']} Operation cancelled.",
    },

    # === PDF: Merge ===
    "pdf.merge.prompt": {
        "ru": (
            f"{E['plus']} <b>Объединение PDF</b>\n\n"
            "Пришли <b>PDF файлы по одному</b> (минимум 2).\n"
            "Когда закончишь — нажми «Склеить»."
        ),
        "uz": (
            f"{E['plus']} <b>PDF birlashtirish</b>\n\n"
            "<b>PDF fayllarni bittalab</b> yubor (kamida 2 ta).\n"
            "Tugagach — «Birlashtirish» tugmasini bos."
        ),
        "en": (
            f"{E['plus']} <b>Merge PDF</b>\n\n"
            "Send <b>PDF files one by one</b> (minimum 2).\n"
            "When done — tap «Merge»."
        ),
    },
    "pdf.merge.received": {
        "ru": f"{E['check']} Принято файлов: <b>{{count}}</b>",
        "uz": f"{E['check']} Qabul qilingan fayllar: <b>{{count}}</b>",
        "en": f"{E['check']} Files received: <b>{{count}}</b>",
    },
    "pdf.merge.need_more": {
        "ru": f"{E['info']} Пришли ещё хотя бы один PDF.",
        "uz": f"{E['info']} Yana kamida bitta PDF yubor.",
        "en": f"{E['info']} Send at least one more PDF.",
    },
    "pdf.merge.processing": {
        "ru": f"{E['gear']} Склеиваю {{count}} файлов...",
        "uz": f"{E['gear']} {{count}} ta fayl birlashtirilmoqda...",
        "en": f"{E['gear']} Merging {{count}} files...",
    },
    "pdf.merge.done": {
        "ru": f"{E['check']} <b>Готово!</b> Склеено файлов: {{count}}",
        "uz": f"{E['check']} <b>Tayyor!</b> Birlashtirilgan fayllar: {{count}}",
        "en": f"{E['check']} <b>Done!</b> Merged files: {{count}}",
    },

    # === PDF: Split ===
    "pdf.split.prompt_file": {
        "ru": f"{E['edit']} <b>Разделение PDF</b>\n\nПришли PDF файл.",
        "uz": f"{E['edit']} <b>PDF bo'lish</b>\n\nPDF faylni yubor.",
        "en": f"{E['edit']} <b>Split PDF</b>\n\nSend a PDF file.",
    },
    "pdf.split.prompt_mode": {
        "ru": (
            f"{E['info']} Файл принят. Страниц: <b>{{pages}}</b>\n\n"
            "Как разделить?"
        ),
        "uz": (
            f"{E['info']} Fayl qabul qilindi. Sahifalar: <b>{{pages}}</b>\n\n"
            "Qanday bo'lamiz?"
        ),
        "en": (
            f"{E['info']} File received. Pages: <b>{{pages}}</b>\n\n"
            "How to split?"
        ),
    },
    "pdf.split.prompt_ranges": {
        "ru": (
            f"{E['edit']} Пришли диапазоны страниц.\n\n"
            "Формат: <code>1-5, 7, 10-12</code>\n"
            "Всего страниц: <b>{pages}</b>"
        ),
        "uz": (
            f"{E['edit']} Sahifa diapazonlarini yubor.\n\n"
            "Format: <code>1-5, 7, 10-12</code>\n"
            "Jami sahifalar: <b>{pages}</b>"
        ),
        "en": (
            f"{E['edit']} Send page ranges.\n\n"
            "Format: <code>1-5, 7, 10-12</code>\n"
            "Total pages: <b>{pages}</b>"
        ),
    },
    "pdf.split.processing": {
        "ru": f"{E['gear']} Разделяю PDF...",
        "uz": f"{E['gear']} PDF bo'linmoqda...",
        "en": f"{E['gear']} Splitting PDF...",
    },
    "pdf.split.done": {
        "ru": f"{E['check']} <b>Готово!</b> Создано файлов: {{count}}",
        "uz": f"{E['check']} <b>Tayyor!</b> Yaratilgan fayllar: {{count}}",
        "en": f"{E['check']} <b>Done!</b> Files created: {{count}}",
    },

    # === PDF: Compress ===
    "pdf.compress.prompt_file": {
        "ru": f"{E['package']} <b>Сжатие PDF</b>\n\nПришли PDF файл.",
        "uz": f"{E['package']} <b>PDF siqish</b>\n\nPDF faylni yubor.",
        "en": f"{E['package']} <b>Compress PDF</b>\n\nSend a PDF file.",
    },
    "pdf.compress.prompt_level": {
        "ru": f"{E['info']} Выбери уровень сжатия:",
        "uz": f"{E['info']} Siqish darajasini tanla:",
        "en": f"{E['info']} Choose a compression level:",
    },
    "pdf.compress.processing": {
        "ru": f"{E['gear']} Сжимаю PDF...",
        "uz": f"{E['gear']} PDF siqilmoqda...",
        "en": f"{E['gear']} Compressing PDF...",
    },
    "pdf.compress.done": {
        "ru": (
            f"{E['check']} <b>Готово!</b>\n\n"
            f"Было: <b>{{before}} МБ</b>\n"
            f"Стало: <b>{{after}} МБ</b>\n"
            f"Сжатие: <b>{{percent}}%</b>"
        ),
        "uz": (
            f"{E['check']} <b>Tayyor!</b>\n\n"
            f"Avval: <b>{{before}} MB</b>\n"
            f"Keyin: <b>{{after}} MB</b>\n"
            f"Siqish: <b>{{percent}}%</b>"
        ),
        "en": (
            f"{E['check']} <b>Done!</b>\n\n"
            f"Before: <b>{{before}} MB</b>\n"
            f"After: <b>{{after}} MB</b>\n"
            f"Saved: <b>{{percent}}%</b>"
        ),
    },

    # === PDF: Password ===
    "pdf.password.prompt_file": {
        "ru": f"{E['lock']} <b>Защита паролем</b>\n\nПришли PDF файл.",
        "uz": f"{E['lock']} <b>Parol himoyasi</b>\n\nPDF faylni yubor.",
        "en": f"{E['lock']} <b>Password protection</b>\n\nSend a PDF file.",
    },
    "pdf.password.prompt_action": {
        "ru": f"{E['info']} Файл принят. Что сделать?",
        "uz": f"{E['info']} Fayl qabul qilindi. Nima qilamiz?",
        "en": f"{E['info']} File received. What to do?",
    },
    "pdf.password.prompt_set": {
        "ru": (
            f"{E['edit']} Пришли <b>пароль</b> для защиты PDF.\n\n"
            f"{E['warning']} Это сообщение лучше удалить после обработки."
        ),
        "uz": (
            f"{E['edit']} PDF himoyasi uchun <b>parol</b> yubor.\n\n"
            f"{E['warning']} Ishlovdan keyin bu xabarni o'chirib tashla."
        ),
        "en": (
            f"{E['edit']} Send a <b>password</b> to protect the PDF.\n\n"
            f"{E['warning']} Delete this message after processing."
        ),
    },
    "pdf.password.prompt_remove": {
        "ru": f"{E['edit']} Пришли <b>пароль</b> для снятия защиты.",
        "uz": f"{E['edit']} Himoyani olib tashlash uchun <b>parolni</b> yubor.",
        "en": f"{E['edit']} Send the <b>password</b> to remove protection.",
    },
    "pdf.password.done_set": {
        "ru": f"{E['check']} <b>PDF защищён паролем.</b>",
        "uz": f"{E['check']} <b>PDF parol bilan himoyalandi.</b>",
        "en": f"{E['check']} <b>PDF protected with password.</b>",
    },
    "pdf.password.done_remove": {
        "ru": f"{E['check']} <b>Защита снята.</b>",
        "uz": f"{E['check']} <b>Himoya olib tashlandi.</b>",
        "en": f"{E['check']} <b>Protection removed.</b>",
    },
    "pdf.password.not_encrypted": {
        "ru": f"{E['info']} Этот PDF и так не защищён паролем.",
        "uz": f"{E['info']} Bu PDF parol bilan himoyalangan emas.",
        "en": f"{E['info']} This PDF is not password-protected.",
    },

    # === PDF: to Images ===
    "pdf.to_images.prompt_file": {
        "ru": f"{E['camera']} <b>PDF в изображения</b>\n\nПришли PDF файл.",
        "uz": f"{E['camera']} <b>PDF rasmlarga</b>\n\nPDF faylni yubor.",
        "en": f"{E['camera']} <b>PDF to Images</b>\n\nSend a PDF file.",
    },
    "pdf.to_images.prompt_quality": {
        "ru": f"{E['info']} Выбери качество (DPI):",
        "uz": f"{E['info']} Sifatni tanla (DPI):",
        "en": f"{E['info']} Choose quality (DPI):",
    },
    "pdf.to_images.confirm_large": {
        "ru": (
            f"{E['warning']} В файле <b>{{pages}} страниц</b>.\n\n"
            "Обработка займёт много времени и памяти. Продолжить?"
        ),
        "uz": (
            f"{E['warning']} Faylda <b>{{pages}} sahifa</b> bor.\n\n"
            "Ishlov ko'p vaqt va xotira oladi. Davom etamizmi?"
        ),
        "en": (
            f"{E['warning']} The file has <b>{{pages}} pages</b>.\n\n"
            "Processing will take long. Continue?"
        ),
    },
    "pdf.to_images.processing": {
        "ru": f"{E['gear']} Рендерю страницы...",
        "uz": f"{E['gear']} Sahifalar rasmga aylantirilmoqda...",
        "en": f"{E['gear']} Rendering pages...",
    },
    "pdf.to_images.done": {
        "ru": f"{E['check']} <b>Готово!</b> Картинок: {{count}}",
        "uz": f"{E['check']} <b>Tayyor!</b> Rasmlar: {{count}}",
        "en": f"{E['check']} <b>Done!</b> Images: {{count}}",
    },

    # === PDF: from Images ===
    "pdf.from_images.prompt": {
        "ru": (
            f"{E['folder']} <b>Изображения в PDF</b>\n\n"
            "Пришли изображения (фото или файлом). Когда закончишь — нажми «Создать PDF»."
        ),
        "uz": (
            f"{E['folder']} <b>Rasmlardan PDF</b>\n\n"
            "Rasmlarni yubor (foto yoki fayl sifatida). Tugagach — «PDF yaratish» tugmasini bos."
        ),
        "en": (
            f"{E['folder']} <b>Images to PDF</b>\n\n"
            "Send images (photos or files). When done — tap «Create PDF»."
        ),
    },
    "pdf.from_images.received": {
        "ru": f"{E['check']} Принято изображений: <b>{{count}}</b>",
        "uz": f"{E['check']} Qabul qilingan rasmlar: <b>{{count}}</b>",
        "en": f"{E['check']} Images received: <b>{{count}}</b>",
    },
    "pdf.from_images.processing": {
        "ru": f"{E['gear']} Создаю PDF...",
        "uz": f"{E['gear']} PDF yaratilmoqda...",
        "en": f"{E['gear']} Creating PDF...",
    },
    "pdf.from_images.done": {
        "ru": f"{E['check']} <b>PDF готов!</b>",
        "uz": f"{E['check']} <b>PDF tayyor!</b>",
        "en": f"{E['check']} <b>PDF ready!</b>",
    },

    # === PDF: Extract text ===
    "pdf.extract.prompt": {
        "ru": f"{E['book']} <b>Извлечение текста</b>\n\nПришли PDF файл.",
        "uz": f"{E['book']} <b>Matn ajratish</b>\n\nPDF faylni yubor.",
        "en": f"{E['book']} <b>Extract text</b>\n\nSend a PDF file.",
    },
    "pdf.extract.processing": {
        "ru": f"{E['gear']} Извлекаю текст...",
        "uz": f"{E['gear']} Matn ajratilmoqda...",
        "en": f"{E['gear']} Extracting text...",
    },
    "pdf.extract.done": {
        "ru": f"{E['check']} <b>Готово!</b> Символов: {{chars}}",
        "uz": f"{E['check']} <b>Tayyor!</b> Belgilar: {{chars}}",
        "en": f"{E['check']} <b>Done!</b> Characters: {{chars}}",
    },

    # === Доп. кнопки для PDF FSM ===
    "btn.do_merge": {"ru": "Склеить", "uz": "Birlashtirish", "en": "Merge"},
    "btn.add_more": {"ru": "Добавить ещё", "uz": "Yana qo'shish", "en": "Add more"},
    "btn.cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.per_page": {"ru": "Каждую страницу", "uz": "Har bir sahifa", "en": "Each page"},
    "btn.by_ranges": {"ru": "По диапазонам", "uz": "Diapazonlar bo'yicha", "en": "By ranges"},
    "btn.compress_low": {"ru": "Слабое", "uz": "Past", "en": "Low"},
    "btn.compress_medium": {"ru": "Среднее", "uz": "O'rta", "en": "Medium"},
    "btn.compress_high": {"ru": "Сильное", "uz": "Kuchli", "en": "High"},
    "btn.set_password": {"ru": "Установить пароль", "uz": "Parol o'rnatish", "en": "Set password"},
    "btn.remove_password": {"ru": "Снять пароль", "uz": "Parolni olib tashlash", "en": "Remove password"},
    "btn.dpi_150": {"ru": "150 dpi", "uz": "150 dpi", "en": "150 dpi"},
    "btn.dpi_300": {"ru": "300 dpi", "uz": "300 dpi", "en": "300 dpi"},
    "btn.dpi_600": {"ru": "600 dpi", "uz": "600 dpi", "en": "600 dpi"},
    "btn.continue": {"ru": "Продолжить", "uz": "Davom etish", "en": "Continue"},
    "btn.create_pdf": {"ru": "Создать PDF", "uz": "PDF yaratish", "en": "Create PDF"},
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод по ключу и языку"""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("ru", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def detect_language(language_code: str | None) -> str:
    """Определяет язык по Telegram: ru → русский, uz → узбекский, остальное → английский"""
    if not language_code:
        return "en"
    if language_code.startswith("ru"):
        return "ru"
    if language_code.startswith("uz"):
        return "uz"
    return "en"
