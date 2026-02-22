from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Category


async def list_active_categories(session: AsyncSession) -> list[Category]:
    stmt = (
        select(Category)
        .where(Category.is_active.is_(True))
        .order_by(Category.sort_order.asc(), Category.id.asc())
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())