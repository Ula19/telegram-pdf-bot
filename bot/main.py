"""Точка входа — запуск PDF-бота"""
import asyncio
import logging
import os
import sys

# uvloop ускоряет asyncio в 2-4 раза (не работает на Windows!)
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass  # на Windows — работаем без uvloop

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings

# настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Инициализация и запуск бота"""
    # подключаемся к Local Bot API если указан URL (снимает лимит 20 МБ → до 2 ГБ)
    session = None
    api_url = settings.bot_api_url
    if api_url != "https://api.telegram.org":
        session = AiohttpSession(
            api=TelegramAPIServer.from_base(api_url, is_local=True),
            timeout=600,  # 10 минут на запрос — большие PDF качаются долго
        )
        logger.info(f"Local Bot API: {api_url}")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session,
    )
    dp = Dispatcher(storage=MemoryStorage())

    # подключаем хэндлеры (порядок важен!)
    from bot.handlers import start, admin, pdf
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(pdf.router)

    # подключаем мидлвари
    from bot.middlewares.rate_limit import RateLimitMiddleware
    from bot.middlewares.subscription import SubscriptionMiddleware

    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    async def _background_cleanup() -> None:
        """Фоновая задача: очистка памяти и дисков каждые 5 минут.

        - rate_limit: протухшие записи в памяти
        - /tmp/pdfbot_*: подвисшие tmp-папки старше 1 часа (сироты от зависших FSM)
        - /var/lib/telegram-bot-api: файлы, которые bot-api не смог удалить
          точечной чисткой (старше 1 часа — как в эталоне bot_4_youtube)
        """
        import glob
        import os
        import time
        from bot.middlewares.rate_limit import cleanup_stale_entries
        while True:
            await asyncio.sleep(300)  # 5 минут
            # 1) rate limit
            removed = cleanup_stale_entries()
            if removed:
                logger.info("Фоновая очистка: удалено %d записей rate limit", removed)

            now = time.time()

            # 2) подвисшие pdfbot_* tmp-папки старше 1 часа
            tmp_cutoff = now - 60 * 60
            tmp_cleaned = 0
            import tempfile as _tf
            import shutil as _sh
            for d in glob.glob(f"{_tf.gettempdir()}/pdfbot_*"):
                try:
                    if os.path.isdir(d) and os.path.getmtime(d) < tmp_cutoff:
                        _sh.rmtree(d, ignore_errors=True)
                        tmp_cleaned += 1
                except OSError:
                    pass
            if tmp_cleaned:
                logger.info("Фоновая очистка: удалено %d подвисших tmp-директорий", tmp_cleaned)

            # 3) осиротевшие файлы Local Bot API (старше 1 часа)
            bot_api_cutoff = now - 60 * 60
            bot_api_cleaned = 0
            for f in glob.glob("/var/lib/telegram-bot-api/**/*", recursive=True):
                try:
                    if os.path.isfile(f) and os.path.getmtime(f) < bot_api_cutoff:
                        os.remove(f)
                        bot_api_cleaned += 1
                except OSError:
                    pass
            if bot_api_cleaned:
                logger.info("Фоновая очистка: удалено %d файлов Local Bot API", bot_api_cleaned)

    @dp.startup()
    async def on_startup() -> None:
        # чистим сиротские временные директории от прошлых запусков
        # (если бота прибили SIGKILL, TemporaryDirectory-финализаторы не отработали)
        import glob
        import shutil
        import tempfile
        orphan_count = 0
        for old in glob.glob(f"{tempfile.gettempdir()}/pdfbot_*"):
            shutil.rmtree(old, ignore_errors=True)
            orphan_count += 1
        if orphan_count:
            logger.info("Очищено %d сиротских tmp-директорий", orphan_count)

        # создаём таблицы в БД
        from bot.database import engine
        from bot.database.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы БД созданы")

        # запускаем фоновую очистку
        asyncio.create_task(_background_cleanup())
        logger.info("Фоновая очистка запущена (интервал 5 мин)")

        bot_info = await bot.get_me()
        logger.info(f"Бот @{bot_info.username} запущен!")

        # ставим дефолтное меню команд (глобально, ru — для новых юзеров)
        from bot.utils.commands import set_default_commands
        await set_default_commands(bot)
        logger.info("Дефолтное меню команд установлено")

    @dp.shutdown()
    async def on_shutdown() -> None:
        logger.info("Бот остановлен")

    # запускаем polling
    try:
        logger.info("Запуск polling...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
