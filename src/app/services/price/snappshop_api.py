import httpx
from app.services.price.base import PriceResult

class SnappshopApiFetcher:
    def __init__(self, timeout_seconds: float = 10.0) -> None:
        self._timeout = timeout_seconds

    async def fetch_price(self, api_url: str, seller_name: str, headers: dict[str, str] | None = None) -> PriceResult:
        seller_name = (seller_name or "").strip()
        if not seller_name:
            return PriceResult(ok=False, error="seller_name_required")

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                headers=headers or {"User-Agent": "Mozilla/5.0"},
                follow_redirects=True,
                trust_env=False,
            ) as client:
                r = await client.get(api_url)
                r.raise_for_status()
                data = r.json()
        except Exception as e:
            return PriceResult(ok=False, error=f"http_error: {type(e).__name__}: {e}")

        # TODO: وقتی endpoint را دادی، اینجا json parsing دقیق را می‌گذاریم
        # باید داخل data فروشنده‌ها/offerها را پیدا کنیم و قیمت فروشنده موردنظر را استخراج کنیم.

        return PriceResult(ok=False, error="json_parser_not_implemented")