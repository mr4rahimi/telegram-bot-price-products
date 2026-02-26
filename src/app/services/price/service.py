from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Offer, OfferPlatform
from app.services.price.basalam import BasalamFetcher
from app.services.price.snappshop import SnappshopFetcher


def _utcnow_naive() -> datetime:
    # datetime بدون timezone (UTC)
    return datetime.utcnow()


class PriceService:
    def __init__(self) -> None:
        self._basalam = BasalamFetcher()
        self._snappshop = SnappshopFetcher()

    async def get_offer_price_toman(
        self,
        session: AsyncSession,
        offer: Offer,
        force_refresh: bool = False,
    ) -> tuple[int | None, str | None]:

        # TTL check (naive)
        if (
            not force_refresh
            and offer.price_last is not None
            and offer.price_updated_at is not None
        ):
            age = _utcnow_naive() - offer.price_updated_at  
            if age < timedelta(seconds=offer.ttl_seconds):
                return offer.price_last, None

        # Fetch
        if offer.platform == OfferPlatform.basalam:
            result = await self._basalam.fetch_price(offer.url)

        elif offer.platform == OfferPlatform.snappshop:
            result = await self._snappshop.fetch_price(
                offer.url,
                offer.seller_name or "",
            )

        else:
            return offer.price_last, None

        # Persist
        if result.ok and result.price_toman:
            offer.price_last = result.price_toman
            offer.price_updated_at = _utcnow_naive()  # ✅ naive
            offer.last_error = None
            await session.commit()
            return offer.price_last, None

        offer.last_error = result.error or "unknown_error"
        await session.commit()

        if offer.price_last is not None:
            return offer.price_last, f"update_failed: {offer.last_error}"

        return None, f"update_failed: {offer.last_error}"