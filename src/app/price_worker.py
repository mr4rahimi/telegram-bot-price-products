import asyncio
import time
from datetime import datetime

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models import Offer
from app.services.price.service import PriceService

# ==============================
#  CONFIG
# ==============================
CONCURRENCY = 5
RETRY_COUNT = 2
DELAY_BETWEEN_REQUEST = 0.3
UPDATE_INTERVAL_SECONDS = 8 * 60 * 60  # 8 hours

price_service = PriceService()


# ==============================
# process single offer
# ==============================
async def process_offer(offer: Offer):
    for attempt in range(RETRY_COUNT + 1):
        try:
            async with AsyncSessionLocal() as session:
                price, err = await price_service._fetch_and_persist(session, offer)

            if price:
                print(f"[OK] Offer {offer.id} → {price:,} تومان")
                return True
            else:
                print(f"[WARN] Offer {offer.id} → {err}")

        except Exception as e:
            print(f"[ERROR] Offer {offer.id} → {type(e).__name__}: {e}")

        if attempt < RETRY_COUNT:
            await asyncio.sleep(1)

    return False


# ==============================
#  update all offers
# ==============================
async def update_all_prices():
    print("\n==============================")
    print(f"[START] {datetime.now()}")
    start_time = time.time()

    success = 0
    failed = 0

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Offer).where(Offer.is_active == True)
        )
        offers = result.scalars().all()

    print(f"[INFO] total offers: {len(offers)}")

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def worker(offer: Offer):
        nonlocal success, failed

        async with semaphore:
            ok = await process_offer(offer)

            if ok:
                success += 1
            else:
                failed += 1

            await asyncio.sleep(DELAY_BETWEEN_REQUEST)

  
    await asyncio.gather(*(worker(o) for o in offers))

    duration = round(time.time() - start_time, 2)

    print("\n[DONE]")
    print(f"success={success}")
    print(f"failed={failed}")
    print(f"duration={duration}s")
    print("==============================\n")



# ==============================
#  LOOP MODE
# ==============================
async def run_forever():
    while True:
        await update_all_prices()
        print(f"[SLEEP] {UPDATE_INTERVAL_SECONDS} seconds...\n")
        await asyncio.sleep(UPDATE_INTERVAL_SECONDS)


# ==============================
#  ENTRY
# ==============================
if __name__ == "__main__":
    import sys

    if "--once" in sys.argv:
        asyncio.run(update_all_prices())
    else:
        asyncio.run(run_forever())