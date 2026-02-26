import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.bot.dispatcher import setup_dispatcher


async def main() -> None:
    if not settings.bot_token or settings.bot_token == "PUT_YOUR_TOKEN_HERE":
        raise RuntimeError("BOT_TOKEN is not set in .env")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = setup_dispatcher()

    await dp.start_polling(
        bot,
        polling_timeout=60,
        request_timeout=30,
        backoff_config={
            "min_delay": 1.0,
            "max_delay": 20.0,
            "factor": 1.5,
            "jitter": 0.1,
        },
    )


if __name__ == "__main__":
    asyncio.run(main())