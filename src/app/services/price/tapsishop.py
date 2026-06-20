import re
import httpx

from app.services.price.base import PriceResult

_IDS_URL = "https://ids.tapsi.shop/authCustomer/NewUnknownToken"
_API_BASE = "https://qcommercegw.tapsi.shop"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://tapsi.shop",
    "Referer": "https://tapsi.shop/",
    "client-name": "qcommerce.tapsi.shop",
}


class TapsiShopFetcher:
    def __init__(self, timeout_seconds: float = 15.0) -> None:
        self._timeout = timeout_seconds

    def _extract_ids(self, product_url: str) -> tuple[str | None, str | None]:
        """Extract (hsin, store_id) from a tapsi.shop product URL."""
        m = re.search(r"tapsi\.shop/product/(\d+)", product_url)
        hsin = m.group(1) if m else None

        m2 = re.search(r"store_id=(\d+)", product_url)
        store_id = m2.group(1) if m2 else None

        return hsin, store_id

    async def _get_guest_token(self, client: httpx.AsyncClient) -> str | None:
        try:
            r = await client.post(_IDS_URL, params={"cityId": ""}, json={})
            r.raise_for_status()
            return r.json().get("token")
        except Exception:
            return None

    async def fetch_price(self, product_url: str) -> PriceResult:
        hsin, store_id = self._extract_ids(product_url)

        if not hsin:
            return PriceResult(ok=False, error="invalid_product_url")
        if not store_id:
            return PriceResult(ok=False, error="store_id_missing_in_url")

        try:
            async with httpx.AsyncClient(
                headers=_HEADERS,
                timeout=self._timeout,
                follow_redirects=True,
                trust_env=False,
            ) as client:
                token = await self._get_guest_token(client)
                if not token:
                    return PriceResult(ok=False, error="guest_token_failed")

                r = await client.get(
                    f"{_API_BASE}/Product/Detail/{hsin}",
                    params={"storeId": store_id},
                    headers={**_HEADERS, "Authorization": f"Bearer {token}"},
                )
                r.raise_for_status()
                payload = r.json()

        except Exception as e:
            return PriceResult(ok=False, error=f"http_error: {type(e).__name__}: {e}")

        products = (payload.get("data") or {}).get("uniqueProducts") or []
        if not products:
            return PriceResult(ok=False, error="no_products_in_response")

        # find matching hsin first, fallback to lowest finalPrice
        best_price = None
        for p in products:
            if str(p.get("hsin")) == hsin:
                price = p.get("finalPrice") or p.get("originalPrice")
                if price and float(price) > 0:
                    return PriceResult(ok=True, price_toman=int(float(price)))

            price = p.get("finalPrice") or p.get("originalPrice")
            if price and float(price) > 0:
                candidate = int(float(price))
                if best_price is None or candidate < best_price:
                    best_price = candidate

        if best_price:
            return PriceResult(ok=True, price_toman=best_price)

        return PriceResult(ok=False, error="price_not_found")
