from app.db.models import OfferPlatform, Product


def format_toman(price: int | None) -> str:
    if price is None:
        return "ناموجود"
    return f"{price:,} تومان"


def format_product_detail(product, prices_by_platform):
    parts = []
    parts.append(f"🛍️ <b>{product.title}</b>")

    if product.description:
        parts.append("")
        parts.append(product.description)

    parts.append("")
    parts.append("💰 قیمت‌ها:")

   
    if "mymonta" in prices_by_platform:
        parts.append(f"▫️ سایت ما: {prices_by_platform['mymonta']}")

    if "basalam" in prices_by_platform:
        parts.append(f"▫️ باسلام: {prices_by_platform['basalam']}")

    if "snappshop" in prices_by_platform:
        parts.append(f"▫️ اسنپ‌شاپ: {prices_by_platform['snappshop']}")

    if "tapsishop" in prices_by_platform:
        parts.append(f"▫️ تپسی‌شاپ: {prices_by_platform['tapsishop']}")

    if "direct" in prices_by_platform:
        parts.append(f"▫️ خرید مستقیم: {prices_by_platform['direct']}")

 
    if len(prices_by_platform) == 0:
        parts.append("ناموجود")

    return "\n".join(parts)