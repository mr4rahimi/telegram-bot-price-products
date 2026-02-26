from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.ui.keyboards import products_kb, product_detail_kb, categories_kb
from app.bot.ui.messages import format_product_detail
from app.db.models import OfferPlatform
from app.db.session import AsyncSessionLocal
from app.repositories.categories import list_active_categories
from app.repositories.products import list_active_products_by_category, get_active_product
from app.repositories.offers import list_active_offers_for_product

from app.services.price.service import PriceService
from app.bot.ui.messages import format_toman

router = Router()


price_service = PriceService()

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

        prices_by_platform: dict[str, str] = {}
        offer_links: list[tuple[str, str]] = []

        # Basalam: fetch with TTL + cache
        for off in offers:
            if off.platform == OfferPlatform.basalam:
                price, err = await price_service.get_offer_price_toman(session, off)
                if err and price is not None:
                    prices_by_platform["basalam"] = f"{format_toman(price)} (آخرین ذخیره، خطا در بروزرسانی)"
                elif err and price is None:
                    prices_by_platform["basalam"] = "ناموجود (خطا در دریافت)"
                else:
                    prices_by_platform["basalam"] = format_toman(price)

        
            if off.platform == OfferPlatform.snappshop:
              price, err = await price_service.get_offer_price_toman(session, off)
            if err and price is not None:
              prices_by_platform["snappshop"] = f"{format_toman(price)} (آخرین ذخیره، خطا در بروزرسانی)"
            elif err and price is None:
              prices_by_platform["snappshop"] = "ناموجود (خطا در دریافت)"
            else:
              prices_by_platform["snappshop"] = format_toman(price)
            if off.platform == OfferPlatform.direct:
                prices_by_platform.setdefault("direct", "—")

            label = {
                OfferPlatform.basalam: "🔗 باسلام",
                OfferPlatform.snappshop: "🔗 اسنپ‌شاپ",
                OfferPlatform.direct: "🔗 خرید مستقیم",
            }.get(off.platform, f"🔗 {off.platform.value}")
            offer_links.append((label, off.url))

    text = format_product_detail(product, prices_by_platform)

    category_id = product.category_id
    kb = product_detail_kb(offer_links=offer_links, category_id=category_id)

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