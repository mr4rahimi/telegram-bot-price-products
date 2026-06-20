import re
import httpx
from app.services.price.base import PriceResult


class BasalamFetcher:
    def __init__(self, timeout_seconds: float = 20.0) -> None:
        self._timeout = timeout_seconds

    async def fetch_price(self, url: str) -> PriceResult:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "fa-IR,fa;q=0.9",
            "Connection": "keep-alive",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                headers=headers,
                follow_redirects=True,
            ) as client:
                r = await client.get(url)

                if r.status_code != 200:
                    return PriceResult(ok=False, error=f"status_{r.status_code}")

                text = r.text

        except Exception as e:
            return PriceResult(ok=False, error=f"http_error: {type(e).__name__}: {e}")

      
        matches = re.findall(
            r'"price"\s*:\s*([0-9]+)',
            text
        )
        if matches:
            price = int(matches[0]) // 10
            if price > 0:
                return PriceResult(ok=True, price_toman=price)

        # 🔥 روش 2: fallback ساده
        matches2 = re.findall(r"(\d{3,})\s*تومان", text)
        if matches2:
            price = int(matches2[0].replace(",", ""))
            return PriceResult(ok=True, price_toman=price)

        return PriceResult(ok=False, error="price_not_found")