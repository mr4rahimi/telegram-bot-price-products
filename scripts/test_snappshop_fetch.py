import asyncio
from app.services.price.snappshop import SnappshopFetcher


async def main():
    url = "https://snappshop.ir/product/snp-195803973"
    seller = "ابزار الکتریکی پیمان"  
    res = await SnappshopFetcher().fetch_price(url, seller)
    print(res)


if __name__ == "__main__":
    asyncio.run(main())