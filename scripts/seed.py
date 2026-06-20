import asyncio
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models import Category, Product, Offer, OfferPlatform


async def seed():
    async with AsyncSessionLocal() as session:
     
        existing = await session.execute(select(Category).limit(1))
        if existing.scalar_one_or_none():
            print("Seed skipped: data already exists.")
            return

        cat = Category(title="شیر ظرفشویی", description="دسته نمونه برای تست دو", sort_order=0)
        session.add(cat)
        await session.flush()  

        prod = Product(
            category_id=cat.id,
            title="شیر ظرفشویی مدل فنری طلایی",
            description="توضیحات فنری نمونه",
            features_json=[{"k": "جنس", "v": "برنج"}, {"k": "رنگ", "v": "کروم"}],
        )
        session.add(prod)
        await session.flush()

        session.add_all([
            Offer(
                product_id=prod.id,
                platform=OfferPlatform.basalam,
                url="https://basalam.com/erfan_salt/product/27337897",
            ),
            Offer(
                product_id=prod.id,
                platform=OfferPlatform.snappshop,
                url="https://snappshop.ir/product/snp-900635467",
                vendor_id="نام فروشنده شما",
            ),
            Offer(
                product_id=prod.id,
                platform=OfferPlatform.direct,
                url="https://example.com/product/test",
            ),
        ])

        await session.commit()
        print("Seed done.")


if __name__ == "__main__":
    asyncio.run(seed())