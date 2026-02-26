import asyncio

from aiohttp import ClientTimeout
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from app.config import settings


async def main():
    session = AiohttpSession(
        proxy="http://127.0.0.1:10808/",
        timeout=ClientTimeout(total=60),
    )
    bot = Bot(
        token=settings.bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    me = await bot.get_me()
    print(me)


if __name__ == "__main__":
    asyncio.run(main())