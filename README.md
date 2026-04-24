# bot_4_pdf — Telegram PDF-бот

Бот для работы с PDF файлами прямо в Telegram.

## Возможности

- Объединить несколько PDF в один
- Разделить PDF на страницы или диапазоны
- Сжать PDF (через Ghostscript)
- Установить/снять пароль на PDF
- Конвертировать PDF в изображения и обратно
- Извлечь текст из PDF

## Стек

- Python 3.12, aiogram 3.26
- PostgreSQL (SQLAlchemy + asyncpg)
- pypdf, pikepdf, pdf2image, Pillow
- Ghostscript (сжатие), poppler-utils (рендер)
- Local Bot API (файлы до 2 ГБ вместо 20 МБ)
- Docker + docker-compose

## Быстрый старт

1. Заполнить `.env`:

```bash
cp .env.example .env
# BOT_TOKEN      — от @BotFather
# API_ID/API_HASH — с https://my.telegram.org (для Local Bot API)
# BOT_API_PORT   — уникальный порт для контейнера bot-api
# DB_PASSWORD
# ADMIN_IDS      — Telegram ID через запятую
```

2. Запустить:

```bash
docker compose up -d --build
docker compose logs -f bot
```

В логах должно появиться `Local Bot API: http://bot-api:8081`.

## Структура

```
bot/
├── main.py          # entrypoint, сессия Local Bot API, фоновая очистка
├── config.py        # настройки из .env
├── i18n.py          # переводы ru/uz/en
├── emojis.py        # кастомные эмодзи для кнопок/текста
├── handlers/
│   ├── start.py     # /start, меню, профиль, язык, подписка, /cancel
│   ├── admin.py     # админка: статистика, каналы, рассылка
│   └── pdf.py       # FSM для 7 PDF-операций
├── services/
│   └── pdf.py       # PdfService: merge/split/compress/password/…
├── keyboards/       # inline, admin
├── middlewares/     # rate_limit (5/мин), subscription
├── database/        # User, Channel (SQLAlchemy async)
└── utils/           # commands, helpers
```

## Команды бота

- `/start` — запустить бота
- `/menu` — главное меню
- `/profile` — профиль
- `/help` — помощь
- `/language` — сменить язык
- `/cancel` — отменить текущее действие

## Очистка диска

- После скачивания каждого файла — сразу удаляем исходник из `bot-api` volume.
- Раз в час — фоновый GC: сносим всё из `/var/lib/telegram-bot-api` и
  `/tmp/pdfbot_*` старше 1 часа (страховка от сирот).
- `tempfile.mkdtemp` на каждую операцию, `shutil.rmtree` во всех ветках
  (успех / ошибка / отмена / `/cancel` / `/start`).
