import asyncio
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models import Offer, OfferPlatform
from app.services.price.service import PriceService


async def main():
    svc = PriceService()
    async with AsyncSessionLocal() as session:
        offers = (await session.execute(select(Offer).where(Offer.platform.in_([OfferPlatform.basalam, OfferPlatform.snappshop])))).scalars().all()
        for o in offers:
            price, err = await svc.get_offer_price_toman(session, o, force_refresh=True)
            print(o.platform.value, o.url, o.seller_name, price, err)

if __name__ == "__main__":
    asyncio.run(main())