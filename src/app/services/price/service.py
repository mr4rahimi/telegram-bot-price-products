from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Offer, OfferPlatform

from app.services.price.basalam import BasalamFetcher
from app.services.price.snappshop import SnappshopFetcher
from app.services.price.tapsishop import TapsiShopFetcher
from app.services.price.mymonta import MymontaFetcher


class PriceService:

    def __init__(self) -> None:
        self.basalam = BasalamFetcher()
        self.snappshop = SnappshopFetcher()
        self.tapsishop = TapsiShopFetcher()
        self.mymonta = MymontaFetcher()

    async def _fetch_and_persist(
        self,
        session: AsyncSession,
        offer: Offer,
    ) -> tuple[int | None, str | None]:

        try:

            # -----------------------------
            # BASALAM
            # -----------------------------
            if offer.platform == OfferPlatform.basalam:

                result = await self.basalam.fetch_price(
                    offer.url,
                )

            # -----------------------------
            # SNAPPSHOP
            # -----------------------------
            elif offer.platform == OfferPlatform.snappshop:
                result = await self.snappshop.fetch_price(
                    offer.url,
                    offer.vendor_id,
                )

            # -----------------------------
            # TAPSI SHOP
            # -----------------------------
            elif offer.platform == OfferPlatform.tapsishop:
                result = await self.tapsishop.fetch_price(offer.url)

            # -----------------------------
            # MYMONTA
            # -----------------------------
            elif offer.platform == OfferPlatform.mymonta:
                result = await self.mymonta.fetch_price(offer.url)

            else:
                return None, "unsupported_platform"

            # -----------------------------
            # ERROR
            # -----------------------------
            if not result.ok:
                return None, f"update_failed: {result.error}"

            # -----------------------------
            # SAVE TO DB
            # -----------------------------
            offer.price_last = result.price_toman
            offer.price_updated_at = datetime.utcnow()

            session.add(offer)

            await session.commit()
            await session.refresh(offer)

            return result.price_toman, None

        except Exception as e:

            await session.rollback()

            return None, f"exception: {type(e).__name__}: {e}"