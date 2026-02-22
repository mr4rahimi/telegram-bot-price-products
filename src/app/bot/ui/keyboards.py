from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def categories_kb(categories: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=title, callback_data=f"cat:{cat_id}")]
        for cat_id, title in categories
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def products_kb(products: list[tuple[int, str]], category_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=title, callback_data=f"prod:{prod_id}")]
        for prod_id, title in products
    ]
    rows.append([InlineKeyboardButton(text="⬅️ بازگشت به دسته‌ها", callback_data="back:cats")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def product_detail_kb(offer_links: list[tuple[str, str]], category_id: int) -> InlineKeyboardMarkup:
    """
    offer_links: list of (button_text, url)
    """
    rows = [[InlineKeyboardButton(text=txt, url=url)] for txt, url in offer_links]
    rows.append([InlineKeyboardButton(text="⬅️ بازگشت به محصولات", callback_data=f"back:prods:{category_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)