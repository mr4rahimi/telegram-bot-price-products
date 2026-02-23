import re


_PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def normalize_price_to_toman(value: str | int) -> int | None:
    """
    ورودی می‌تواند مثل:
      "۲۸۵٬۰۰۰ تومان"
      "285,000"
      285000
    خروجی: int (تومان)
    """
    if value is None:
        return None

    if isinstance(value, int):
        return value

    s = str(value).strip()
    if not s:
        return None

    s = s.translate(_PERSIAN_DIGITS).translate(_ARABIC_DIGITS)

   
    digits = re.findall(r"\d+", s)
    if not digits:
        return None

 

    nums = [int(x) for x in digits if x]
    return max(nums) if nums else None