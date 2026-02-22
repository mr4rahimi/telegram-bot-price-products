from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.ui.keyboards import categories_kb
from app.db.session import AsyncSessionLocal
from app.repositories.categories import list_active_categories

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    async with AsyncSessionLocal() as session:
        cats = await list_active_categories(session)

    if not cats:
        await message.answer("هیچ دسته‌بندی فعالی ثبت نشده.")
        return

    kb = categories_kb([(c.id, c.title) for c in cats])
    await message.answer("یکی از دسته‌بندی‌ها را انتخاب کنید:", reply_markup=kb)