from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.ui.keyboards import products_kb, product_detail_kb, categories_kb
from app.bot.ui.messages import format_product_detail
from app.db.models import OfferPlatform
from app.db.session import AsyncSessionLocal
from app.repositories.categories import list_active_categories
from app.repositories.products import list_active_products_by_category, get_active_product
from app.repositories.offers import list_active_offers_for_product

router = Router()


@router.callback_query(F.data.startswith("cat:"))
async def on_category_selected(cb: CallbackQuery) -> None:
    category_id = int(cb.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        products = await list_active_products_by_category(session, category_id)

    if not products:
        await cb.message.edit_text("این دسته فعلاً محصولی ندارد.")
        await cb.answer()
        return

    kb = products_kb([(p.id, p.title) for p in products], category_id=category_id)
    await cb.message.edit_text("یک محصول را انتخاب کنید:", reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("prod:"))
async def on_product_selected(cb: CallbackQuery) -> None:
    product_id = int(cb.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        product = await get_active_product(session, product_id)
        if not product:
            await cb.answer("محصول یافت نشد.", show_alert=True)
            return
        offers = await list_active_offers_for_product(session, product_id)

    text = format_product_detail(product, offers)

    # دکمه لینک‌ها
    offer_links: list[tuple[str, str]] = []
    for off in offers:
        label = {
            OfferPlatform.basalam: "🔗 باسلام",
            OfferPlatform.snappshop: "🔗 اسنپ‌شاپ",
            OfferPlatform.direct: "🔗 خرید مستقیم",
        }.get(off.platform, f"🔗 {off.platform.value}")
        offer_links.append((label, off.url))

    # برای برگشت به محصولات باید category_id را داشته باشیم
    category_id = product.category_id
    kb = product_detail_kb(offer_links=offer_links, category_id=category_id)

    # اگر قبلاً پیام بوده، ادیت کنیم
    await cb.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
    await cb.answer()


@router.callback_query(F.data == "back:cats")
async def back_to_categories(cb: CallbackQuery) -> None:
    async with AsyncSessionLocal() as session:
        cats = await list_active_categories(session)

    if not cats:
        await cb.message.edit_text("هیچ دسته‌بندی فعالی ثبت نشده.")
        await cb.answer()
        return

    kb = categories_kb([(c.id, c.title) for c in cats])
    await cb.message.edit_text("یکی از دسته‌بندی‌ها را انتخاب کنید:", reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("back:prods:"))
async def back_to_products(cb: CallbackQuery) -> None:
    category_id = int(cb.data.split(":")[2])

    async with AsyncSessionLocal() as session:
        products = await list_active_products_by_category(session, category_id)

    if not products:
        await cb.message.edit_text("این دسته فعلاً محصولی ندارد.")
        await cb.answer()
        return

    kb = products_kb([(p.id, p.title) for p in products], category_id=category_id)
    await cb.message.edit_text("یک محصول را انتخاب کنید:", reply_markup=kb)
    await cb.answer()