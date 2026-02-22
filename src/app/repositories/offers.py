from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Offer


async def list_active_offers_for_product(session: AsyncSession, product_id: int) -> list[Offer]:
    stmt = (
        select(Offer)
        .where(
            Offer.is_active.is_(True),
            Offer.product_id == product_id,
        )
        .order_by(Offer.id.asc())
    )
    res = await session.execute(stmt)
    return list(res.scalars().all())