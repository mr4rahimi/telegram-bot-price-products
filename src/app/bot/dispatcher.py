from aiogram import Dispatcher
from aiogram import Router

from app.bot.handlers.start import router as start_router
from app.bot.handlers.catalog import router as catalog_router


def clone_router(router: Router) -> Router:
    new_router = Router()

    # copy handlers
    for handler in router.message.handlers:
        new_router.message.register(handler.callback, *handler.filters)

    for handler in router.callback_query.handlers:
        new_router.callback_query.register(handler.callback, *handler.filters)

    return new_router


def setup_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    # ✅ clone instead of reuse
    dp.include_router(clone_router(start_router))
    dp.include_router(clone_router(catalog_router))

    return dp