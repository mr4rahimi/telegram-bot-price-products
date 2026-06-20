import re
import httpx

from app.services.price.base import PriceResult

_API_BASE = "https://mymonta.ir"


class MymontaFetcher:
    def __init__(self, timeout_seconds: float = 15.0) -> None:
        self._timeout = timeout_seconds

    def _extract_slug(self, product_url: str) -> str | None:
        # https://mymonta.ir/products/some-slug  →  some-slug
        m = re.search(r"mymonta\.ir/products/([^/?#]+)", product_url)
        if m:
            return m.group(1)
        # accept bare slug too (no domain)
        if "/" not in product_url and product_url.strip():
            return product_url.strip()
        return None

    async def fetch_price(self, product_url: str) -> PriceResult:
        slug = self._extract_slug(product_url)
        if not slug:
            return PriceResult(ok=False, error="invalid_product_url")

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
                trust_env=False,
            ) as client:
                r = await client.get(f"{_API_BASE}/api/products/{slug}")
                if r.status_code == 404:
                    return PriceResult(ok=False, error="product_not_found")
                r.raise_for_status()
                data = r.json()

        except Exception as e:
            return PriceResult(ok=False, error=f"http_error: {type(e).__name__}: {e}")

        # price/salePrice are BigInt → serialized as strings
        sale = data.get("salePrice")
        regular = data.get("price")

        def to_int(v) -> int | None:
            try:
                n = int(v)
                return n if n > 0 else None
            except (TypeError, ValueError):
                return None

        price = to_int(sale) or to_int(regular)
        if not price:
            return PriceResult(ok=False, error="price_not_found")

        return PriceResult(ok=True, price_toman=price)
