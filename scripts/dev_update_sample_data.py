import asyncio
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models import Category, Product, Offer, OfferPlatform


async def main():
    async with AsyncSessionLocal() as session:
        
        prod = (await session.execute(select(Product).order_by(Product.id.asc()).limit(1))).scalar_one_or_none()
        if not prod:
            print("No product found.")
            return

        prod.title = "شیر ظرفشویی فنری (نمونه واقعی)"
        prod.description = "تست: نمایش قیمت باسلام و اسنپ‌شاپ"
        await session.flush()

        # update basalam offer
        basalam = (await session.execute(
            select(Offer).where(Offer.product_id == prod.id, Offer.platform == OfferPlatform.basalam).limit(1)
        )).scalar_one_or_none()
        if basalam:
            basalam.url = "https://basalam.com/shiralateirahoora/product/2153761"
            basalam.price_last = None
            basalam.price_updated_at = None
            basalam.last_error = None

        # update snappshop offer
        snapp = (await session.execute(
            select(Offer).where(Offer.product_id == prod.id, Offer.platform == OfferPlatform.snappshop).limit(1)
        )).scalar_one_or_none()
        if snapp:
            snapp.url = "https://snappshop.ir/product/snp-195803973"
            snapp.vendor_id = "ابزار الکتریکی پیمان"  # فعلاً برای تست
            snapp.price_last = None
            snapp.price_updated_at = None
            snapp.last_error = None

        await session.commit()
        print("Updated sample product/offers.")


if __name__ == "__main__":
    asyncio.run(main())