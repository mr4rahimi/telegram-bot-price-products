from dataclasses import dataclass


@dataclass
class PriceResult:
    ok: bool
    price_toman: int | None = None
    error: str | None = None