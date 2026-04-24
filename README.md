# bot_4_pdf — Telegram PDF-бот

Бот для работы с PDF файлами прямо в Telegram.

## Возможности

- Объединить несколько PDF в один
- Разделить PDF на страницы или диапазоны
- Сжать PDF (через Ghostscript)
- Защитить PDF паролем (через pikepdf)
- Конвертировать PDF в изображения и обратно
- Извлечь текст из PDF

## Стек

- Python 3.12, aiogram 3.26
- PostgreSQL (SQLAlchemy + asyncpg)
- pypdf, pikepdf, pdf2image, Pillow
- Docker + docker-compose

## Быстрый старт

```bash
cp .env.example .env
# заполнить .env (BOT_TOKEN, ADMIN_IDS, DB_PASSWORD)
docker compose up -d
```

## Структура

```
bot/
├── main.py          # entrypoint
├── config.py        # настройки из .env
├── i18n.py          # переводы ru/uz/en
├── handlers/        # start, admin, pdf (TODO)
├── services/        # pdf.py (TODO)
├── keyboards/       # inline, admin
├── middlewares/     # rate_limit, subscription
├── database/        # models, crud
└── utils/           # commands, helpers
```

## Команды бота

- `/start` — запустить бота
- `/menu` — главное меню
- `/profile` — профиль
- `/help` — помощь
- `/language` — сменить язык
- `/cancel` — отменить текущее действие
