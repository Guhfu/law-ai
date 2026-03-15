import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from .config import get_bot_settings
from .handlers import router as main_router


async def main() -> None:
    settings = get_bot_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не налаштовано в .env")

    bot = Bot(token=settings.telegram_bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(main_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

