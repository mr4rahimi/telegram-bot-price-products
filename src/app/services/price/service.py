from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Offer, OfferPlatform
from app.services.price.basalam import BasalamFetcher


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PriceService:
    def __init__(self) -> None:
        self._basalam = BasalamFetcher()

    async def get_offer_price_toman(
        self,
        session: AsyncSession,
        offer: Offer,
        force_refresh: bool = False,
    ) -> tuple[int | None, str | None]:
        """
        خروجی: (price_toman, error_message)
        - اگر قیمت موجود باشد error_message=None
        - اگر خطا باشد price ممکن است None یا آخرین قیمت کش شده باشد
        """
        if offer.platform != OfferPlatform.basalam:
            return offer.price_last, None

     
        if not force_refresh and offer.price_last is not None and offer.price_updated_at is not None:
            age = _utcnow() - offer.price_updated_at.replace(tzinfo=timezone.utc)
            if age < timedelta(seconds=offer.ttl_seconds):
                return offer.price_last, None

      
        result = await self._basalam.fetch_price(offer.url)
        if result.ok and result.price_toman:
            offer.price_last = result.price_toman
            offer.price_updated_at = _utcnow()
            offer.last_error = None
            await session.commit()
            return offer.price_last, None
    
        offer.last_error = result.error or "unknown_error"
        await session.commit()

        if offer.price_last is not None:
            return offer.price_last, f"update_failed: {offer.last_error}"

        return None, f"update_failed: {offer.last_error}"