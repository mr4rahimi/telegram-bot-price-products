import re

import httpx

from app.services.price.base import PriceResult


class SnappshopFetcher:
    """
    Snappshop price fetcher
    """

    def __init__(
        self,
        timeout_seconds: float = 10.0,
        lat: float = 35.77331,
        lng: float = 51.418591,
    ) -> None:
        self._timeout = timeout_seconds
        self._lat = lat
        self._lng = lng

    def _extract_product_id(self, product_url: str) -> int | None:
        m = re.search(r"snp-(\d+)", product_url)

        if m:
            return int(m.group(1))

        return None

    def _build_api_url(self, product_id: int) -> str:
        return (
            f"https://apix.snappshop.ir/products/v2/"
            f"{product_id}?lat={self._lat}&lng={self._lng}"
        )

    async def fetch_price(
        self,
        product_url: str,
        vendor_id: str | None = None,
    ) -> PriceResult:

        product_id = self._extract_product_id(product_url)

        if not product_id:
            return PriceResult(
                ok=False,
                error="invalid_product_url",
            )

        api_url = self._build_api_url(product_id)

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": product_url,
            "Origin": "https://snappshop.ir",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                headers=headers,
                follow_redirects=True,
                trust_env=False,
            ) as client:

                response = await client.get(api_url)
                response.raise_for_status()

                payload = response.json()

        except Exception as e:
            return PriceResult(
                ok=False,
                error=f"http_error: {type(e).__name__}: {e}",
            )

        if not payload.get("status"):
            return PriceResult(
                ok=False,
                error="api_status_false",
            )

        data = payload.get("data") or {}
        variants = data.get("variants") or []

        best_price = None

        for variant in variants:

            vendors = variant.get("vendor") or []

            for vp in vendors:

                special_price = int(vp.get("special_price") or 0)
                normal_price = int(vp.get("price") or 0)

                final_price = (
                    special_price
                    if special_price > 0
                    else normal_price
                )

                if final_price <= 0:
                    continue

           
                if best_price is None:
                    best_price = final_price
                else:
                    best_price = min(best_price, final_price)

        if best_price is None:
            return PriceResult(
                ok=False,
                error="price_not_found",
            )

        return PriceResult(
            ok=True,
            price_toman=best_price,
        )