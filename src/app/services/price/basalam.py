import re

import httpx
from lxml import html

from app.services.price.base import PriceResult
from app.services.price.normalize import normalize_price_to_toman


class BasalamFetcher:
    def __init__(self, timeout_seconds: float = 10.0) -> None:
        self._timeout = timeout_seconds

    async def fetch_price(self, url: str) -> PriceResult:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout, headers=headers, follow_redirects=True) as client:
                r = await client.get(url)
                r.raise_for_status()
                text = r.text
        except Exception as e:
            return PriceResult(ok=False, error=f"http_error: {type(e).__name__}: {e}")

        m = re.search(r'"offers"\s*:\s*\{.*?"price"\s*:\s*([0-9]+)', text, flags=re.DOTALL)
        if m:
            irr = int(m.group(1))  # IRR
    
            toman = irr // 10
            if toman > 0:
                return PriceResult(ok=True, price_toman=toman)

        try:
            tree = html.fromstring(text)
            body_text = " ".join(tree.xpath("//body//text()"))
        except Exception as e:
            return PriceResult(ok=False, error=f"parse_error: {type(e).__name__}: {e}")

        price = normalize_price_to_toman(body_text)
        if price and price > 0:
            return PriceResult(ok=True, price_toman=price)

        return PriceResult(ok=False, error="price_not_found")