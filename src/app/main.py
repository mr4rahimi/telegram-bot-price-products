import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.utils.backoff import BackoffConfig

from app.config import settings
from app.bot.dispatcher import setup_dispatcher


async def main() -> None:
    proxy_url = "http://127.0.0.1:10808/"

    
    session = AiohttpSession(
        proxy=proxy_url,
        timeout=60,   # ✅ عدد
    )

    bot = Bot(
        token=settings.bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = setup_dispatcher()

    await dp.start_polling(
        bot,
        polling_timeout=60,
        request_timeout=60,
        backoff_config=BackoffConfig(min_delay=1.0, max_delay=20.0, factor=1.5, jitter=0.1),
    )


if __name__ == "__main__":
    asyncio.run(main())