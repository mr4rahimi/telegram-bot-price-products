import re
from urllib.parse import urlparse

import httpx

from app.services.price.base import PriceResult


class SnappshopFetcher:
    """
    Snappshop price via API:
    https://apix.snappshop.ir/products/v2/{product_id}?lat=...&lng=...
    """

    def __init__(self, timeout_seconds: float = 10.0, lat: float = 35.77331, lng: float = 51.418591) -> None:
        self._timeout = timeout_seconds
        self._lat = lat
        self._lng = lng

    def _extract_product_id(self, product_url: str) -> int | None:
        """
        از لینک‌هایی مثل:
          https://snappshop.ir/product/snp-195803973
        عدد 195803973 را استخراج می‌کند.
        """
        m = re.search(r"snp-(\d+)", product_url)
        if m:
            return int(m.group(1))
        return None

    def _build_api_url(self, product_id: int) -> str:
        return f"https://apix.snappshop.ir/products/v2/{product_id}?lat={self._lat}&lng={self._lng}"

    async def fetch_price(self, product_url: str, seller_name: str) -> PriceResult:
        seller_name = (seller_name or "").strip()
        if not seller_name:
            return PriceResult(ok=False, error="seller_name_required")

        product_id = self._extract_product_id(product_url)
        if not product_id:
            return PriceResult(ok=False, error="invalid_product_url")

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
                r = await client.get(api_url)
                r.raise_for_status()
                payload = r.json()
        except Exception as e:
            return PriceResult(ok=False, error=f"http_error: {type(e).__name__}: {e}")

        if not payload.get("status"):
            return PriceResult(ok=False, error="api_status_false")

        data = payload.get("data") or {}
        vendors = data.get("vendors") or []
        variants = data.get("variants") or []

     
        vendor_id = None
        for v in vendors:
            if (v.get("title") or "").strip() == seller_name:
                vendor_id = v.get("id")
                break

        if not vendor_id:
            return PriceResult(ok=False, error="seller_not_found_in_api")

   
        best_price = None
        for var in variants:
            for vp in (var.get("vendor") or []):
                if vp.get("vendor_id") != vendor_id:
                    continue

                special = int(vp.get("special_price") or 0)
                price = int(vp.get("price") or 0)

                final_price = special if special > 0 else price
                if final_price <= 0:
                    continue


                best_price = final_price
                break
            if best_price:
                break

        if not best_price:
            return PriceResult(ok=False, error="price_not_found_for_seller")

        return PriceResult(ok=True, price_toman=best_price)