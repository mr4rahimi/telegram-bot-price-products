import asyncio
import re
import httpx

async def main():
    url = "https://snappshop.ir/product/snp-195803973"
    seller = "ابزار الکتریکی پیمان"

    async with httpx.AsyncClient(follow_redirects=True, timeout=15, trust_env=False) as client:
        r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        text = r.text

    print("HTML length:", len(text))
    print("Seller present in HTML:", seller in text)

    prices = re.findall(r"\d{1,3}(?:,\d{3})+", text)
    print("Sample price-like strings:", prices[:10])

if __name__ == "__main__":
    asyncio.run(main())