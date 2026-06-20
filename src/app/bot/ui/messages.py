from app.db.models import OfferPlatform, Product


def format_toman(price: int | None) -> str:
    if price is None:
        return "ناموجود"
    return f"{price:,} تومان"


def format_product_detail(product, prices_by_platform):
    parts = []
    parts.append(f"🛍️ {product.title}")

    if product.description:
        parts.append("")
        parts.append(product.description)

    parts.append("")
    parts.append("💰 قیمت‌ها:")

    platform_info = [
        ("mymonta",   "سایت ما"),
        ("basalam",   "باسلام"),
        ("snappshop", "اسنپ‌شاپ"),
        ("tapsishop", "تپسی‌شاپ"),
        ("direct",    "خرید مستقیم"),
    ]

    has_price = False
    for key, label in platform_info:
        if key in prices_by_platform:
            has_price = True
            parts.append(f"▫️ {label}: {prices_by_platform[key]}")

    if not has_price:
        parts.append("ناموجود")

    return "\n".join(parts)
