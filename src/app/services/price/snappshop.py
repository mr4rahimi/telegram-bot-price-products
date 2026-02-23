import re

import httpx
from lxml import html

from app.services.price.base import PriceResult
from app.services.price.normalize import normalize_price_to_toman


class SnappshopFetcher:
    def __init__(self, timeout_seconds: float = 10.0) -> None:
        self._timeout = timeout_seconds

    async def fetch_price(self, url: str, seller_name: str) -> PriceResult:
        """
        قیمت را فقط برای seller_name می‌گیرد.
        اگر فروشنده پیدا نشد: price_not_found_for_seller
        """
        seller_name = (seller_name or "").strip()
        if not seller_name:
            return PriceResult(ok=False, error="seller_name_required")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                headers=headers,
                follow_redirects=True,
                trust_env=False,  
            ) as client:
                r = await client.get(url)
                r.raise_for_status()
                text = r.text
        except Exception as e:
            return PriceResult(ok=False, error=f"http_error: {type(e).__name__}: {e}")

        try:
            tree = html.fromstring(text)
        except Exception as e:
            return PriceResult(ok=False, error=f"parse_error: {type(e).__name__}: {e}")

 
        candidates = tree.xpath(f"//*[normalize-space()={_xpath_literal(seller_name)}]")
        for node in candidates:
          
            container = node
            for _ in range(6):
                if container is None:
                    break
                if container.tag in ("div", "section", "li", "article"):
                    container_text = " ".join(container.xpath(".//text()"))
                    price = _extract_best_price_toman(container_text)
                    if price:
                        return PriceResult(ok=True, price_toman=price)
                container = container.getparent()

    
      
        body_text = " ".join(tree.xpath("//body//text()"))
        idx = body_text.find(seller_name)
        if idx != -1:
            window = body_text[idx : idx + 600] 
            price = _extract_best_price_toman(window)
            if price:
                return PriceResult(ok=True, price_toman=price)

        return PriceResult(ok=False, error="price_not_found_for_seller")


def _extract_best_price_toman(text: str) -> int | None:

    price = normalize_price_to_toman(text)
    if price and price > 0:
        return price
    return None


def _xpath_literal(s: str) -> str:

    if '"' not in s:
        return f'"{s}"'
    if "'" not in s:
        return f"'{s}'"
    parts = s.split('"')
    return "concat(" + ', '.join([f'"{p}"' if i == len(parts) - 1 else f'"{p}", \'"\',' for i, p in enumerate(parts)]).rstrip(",") + ")"