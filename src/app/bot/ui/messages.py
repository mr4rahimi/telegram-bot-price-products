from app.db.models import OfferPlatform, Product, Offer


def format_product_detail(product: Product, offers: list[Offer]) -> str:
    parts: list[str] = []
    parts.append(f"🛍️ <b>{product.title}</b>")

    if product.description:
        parts.append("")
        parts.append(product.description)

    if product.features_json:
        parts.append("")
        parts.append("🔧 <b>ویژگی‌ها</b>")
        # انتظار: [{"k": "...", "v": "..."}, ...]
        for item in product.features_json if isinstance(product.features_json, list) else []:
            k = str(item.get("k", "")).strip()
            v = str(item.get("v", "")).strip()
            if k and v:
                parts.append(f"• {k}: {v}")

    parts.append("")
    parts.append("💳 <b>قیمت</b>: — (در فاز بعدی اضافه می‌شود)")

    parts.append("")
    parts.append("🔗 <b>لینک خرید</b>:")
    for off in offers:
        label = {
            OfferPlatform.basalam: "باسلام",
            OfferPlatform.snappshop: "اسنپ‌شاپ",
            OfferPlatform.direct: "خرید مستقیم",
        }.get(off.platform, off.platform.value)
        parts.append(f"• {label}")

    return "\n".join(parts)