import asyncio

from app.services.price.basalam import BasalamFetcher


async def main():
    url = "https://basalam.com/shiralateirahoora/product/2153761"
    fetcher = BasalamFetcher()
    res = await fetcher.fetch_price(url)
    print(res)


if __name__ == "__main__":
    asyncio.run(main())