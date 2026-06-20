import asyncio
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models import Offer, OfferPlatform
from app.services.price.service import PriceService


async def main():
    svc = PriceService()

    async with AsyncSessionLocal() as session:
        offers = (await session.execute(
            select(Offer).where(Offer.platform.in_([OfferPlatform.basalam, OfferPlatform.snappshop]))
        )).scalars().all()

    for o in offers:
        platform_val = o.platform.value
        url_short = o.url[:60]
        async with AsyncSessionLocal() as session:
            price, err = await svc._fetch_and_persist(session, o)
        print(platform_val, url_short, "→", price, err)

if __name__ == "__main__":
    asyncio.run(main())