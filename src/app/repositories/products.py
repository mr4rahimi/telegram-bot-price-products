from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Product


async def list_active_products_by_category(session: AsyncSession, category_id: int) -> list[Product]:
    stmt = (
        select(Product)
        .where(
            Product.is_active.is_(True),
            Product.category_id == category_id,
        )
        .order_by(Product.id.asc())
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def get_active_product(session: AsyncSession, product_id: int) -> Product | None:
    stmt = select(Product).where(Product.is_active.is_(True), Product.id == product_id)
    res = await session.execute(stmt)
    return res.scalar_one_or_none()