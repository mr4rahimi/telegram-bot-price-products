import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.utils.backoff import BackoffConfig

from app.core.config import settings
from app.bot.dispatcher import setup_dispatcher


async def run_bot(token: str):
    import os

  
    os.environ.pop("http_proxy", None)
    os.environ.pop("https_proxy", None)
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)

    
    session = AiohttpSession(timeout=120)

    from aiogram.client.telegram import TelegramAPIServer

    bot = Bot(
        token=token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        api=TelegramAPIServer.from_base("https://tapi.bale.ai/bot"),
    )

    dp = setup_dispatcher()

    print("🚀 Bot started: BALE")

    try:
        await dp.start_polling(
            bot,
            polling_timeout=120,
            request_timeout=120,
            backoff_config=BackoffConfig(
                min_delay=1.0,
                max_delay=20.0,
                factor=1.5,
                jitter=0.1,
            ),
        )
    except Exception as e:
        print("❌ ERROR:", e)


async def main():
    if not settings.BALE_BOT_TOKEN:
        raise RuntimeError("BALE_BOT_TOKEN not set")

    await run_bot(settings.BALE_BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())