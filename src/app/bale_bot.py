import requests
import asyncio
import os
from pathlib import Path

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.repositories.categories import list_active_categories
from app.repositories.products import list_active_products_by_category, get_active_product
from app.bot.ui.messages import format_product_detail
from app.repositories.offers import list_active_offers_for_product

TOKEN = settings.BALE_BOT_TOKEN
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"



# ---------------- API ----------------

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset

    res = requests.get(url, params=params, timeout=60)
    return res.json()


def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup:
        data["reply_markup"] = reply_markup

    requests.post(url, json=data)


# ---------------- Keyboards ----------------

def categories_kb_bale(categories):
    return {
        "inline_keyboard": [
            [{"text": title, "callback_data": f"cat:{cat_id}"}]
            for cat_id, title in categories
        ]
    }


def products_kb_bale(products, category_id):
    rows = [
        [{"text": title, "callback_data": f"prod:{p_id}"}]
        for p_id, title in products
    ]
    rows.append([{"text": "⬅️ بازگشت", "callback_data": "back:cats"}])
    return {"inline_keyboard": rows}


def product_kb(product):
    rows = []

    if product.mymonta_url and product.mymonta_url.strip():
        rows.append([{"text": "خرید از سایت ما", "url": product.mymonta_url}])

    if product.basalam_url and product.basalam_url.strip():
        rows.append([{"text": "خرید از باسلام", "url": product.basalam_url}])

    if product.snappshop_url and product.snappshop_url.strip():
        rows.append([{"text": "خرید از اسنپ‌شاپ", "url": product.snappshop_url}])

    if product.tapsishop_url and product.tapsishop_url.strip():
        rows.append([{"text": "خرید از تپسی‌شاپ", "url": product.tapsishop_url}])

    if product.website_url and product.website_url.strip():
        rows.append([{"text": "خرید از سایت", "url": product.website_url}])

    rows.append([{"text": "⬅️ بازگشت", "callback_data": f"back:prods:{product.category_id}"}])

    return {"inline_keyboard": rows}



UPLOAD_DIR = str(Path(__file__).resolve().parents[3] / "uploads")


def send_photo(chat_id, image_path, caption=None, reply_markup=None):
    import json
    url = f"{BASE_URL}/sendPhoto"

    filename = image_path.replace("/uploads/", "")
    full_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(full_path):
        print("❌ image not found:", full_path)
        send_message(chat_id, caption or "تصویر یافت نشد")
        return

    with open(full_path, "rb") as f:
        data = {"chat_id": str(chat_id), "parse_mode": "HTML"}
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        requests.post(url, data=data, files={"photo": f})


# ---------------- Handlers ----------------

async def handle_start(chat_id):
    async with AsyncSessionLocal() as session:
        cats = await list_active_categories(session)

    if not cats:
        send_message(chat_id, "هیچ دسته‌بندی فعالی نیست")
        return

    kb = categories_kb_bale([(c.id, c.title) for c in cats])
    send_message(chat_id, "دسته‌بندی‌ها:", kb)


async def handle_category(chat_id, category_id):
    async with AsyncSessionLocal() as session:
        products = await list_active_products_by_category(session, category_id)

    if not products:
        send_message(chat_id, "محصولی وجود ندارد")
        return

    kb = products_kb_bale([(p.id, p.title) for p in products], category_id)
    send_message(chat_id, "محصولات:", kb)


async def handle_product(chat_id, product_id):
    async with AsyncSessionLocal() as session:

        product = await get_active_product(session, product_id)

        if not product:
            send_message(chat_id, "محصول پیدا نشد")
            return

        # ✅ گرفتن offer ها مستقیم از repository
        offers = await list_active_offers_for_product(
            session,
            product_id
        )

        prices_by_platform = {}

        for off in offers:

            if off.price_last is not None:

                platform = off.platform.value
                if platform in ("basalam", "snappshop", "direct", "tapsishop", "mymonta"):
                    prices_by_platform[platform] = f"{off.price_last:,} تومان"

    text = format_product_detail(product, prices_by_platform)

    kb = product_kb(product)

    if product.image_url:
        send_photo(chat_id, product.image_url, text, kb)
    else:
        send_message(chat_id, text, kb)


# ---------------- Main Async Loop ----------------

async def process_update(upd):
    # message
    if "message" in upd:
        msg = upd["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        print("📩", text)

        if text.startswith("/start"):
            await handle_start(chat_id)

    # callback
    elif "callback_query" in upd:
        cb = upd["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        data = cb["data"]

        print("🔘", data)

        if data == "back:cats":
            await handle_start(chat_id)

        elif data.startswith("cat:"):
            cat_id = int(data.split(":")[1])
            await handle_category(chat_id, cat_id)

        elif data.startswith("prod:"):
            prod_id = int(data.split(":")[1])
            await handle_product(chat_id, prod_id)

        elif data.startswith("back:prods:"):
            cat_id = int(data.split(":")[2])
            await handle_category(chat_id, cat_id)


async def main():
    print("🚀 Bale bot started")
    offset = None

    while True:
        try:
            data = get_updates(offset)

            if not data.get("ok"):
                await asyncio.sleep(1)
                continue

            for upd in data["result"]:
                offset = upd["update_id"] + 1
                await process_update(upd)

        except Exception as e:
            print("❌", e)

        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())