from app.db.models import OfferPlatform, Product


def format_toman(price: int | None) -> str:
    if price is None:
        return "ناموجود"
    return f"{price:,} تومان"


def format_product_detail(
    product: Product,
    prices_by_platform: dict[str, str],
) -> str:
    parts: list[str] = []
    parts.append(f"🛍️ <b>{product.title}</b>")

    if product.description:
        parts.append("")
        parts.append(product.description)

    if product.features_json:
        parts.append("")
        parts.append("🔧 <b>ویژگی‌ها</b>")
        if isinstance(product.features_json, list):
            for item in product.features_json:
                k = str(item.get("k", "")).strip()
                v = str(item.get("v", "")).strip()
                if k and v:
                    parts.append(f"• {k}: {v}")

    parts.append("")
    parts.append("💳 <b>قیمت‌ها</b>")
    # کلیدها: basalam/snappshop/direct
    if "basalam" in prices_by_platform:
        parts.append(f"• باسلام: {prices_by_platform['basalam']}")
    if "snappshop" in prices_by_platform:
        parts.append(f"• اسنپ‌شاپ: {prices_by_platform['snappshop']}")
    if "direct" in prices_by_platform:
        parts.append(f"• خرید مستقیم: {prices_by_platform['direct']}")

    return "\n".join(parts)