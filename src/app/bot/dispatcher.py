from aiogram import Dispatcher

from app.bot.handlers.start import router as start_router
from app.bot.handlers.catalog import router as catalog_router


def setup_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(catalog_router)
    return dp