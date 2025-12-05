import asyncio
import time
import httpx

API_URL = "http://127.0.0.1:8000"


async def check_health(client, i):
    start = time.time()
    resp = await client.get(f"{API_URL}/")
    duration = time.time() - start
    print(f"[{i}] Health Check: {resp.status_code} (Took {duration:.4f}s)")


async def trigger_heavy_task(client):
    print("--- Triggering Heavy Monte Carlo Simulation (5M iterations) ---")
    start = time.time()
    # Trigger the backtest endpoint
    resp = await client.post(f"{API_URL}/api/v1/backtest", params={"price": 50000})
    duration = time.time() - start
    print(f"--- Heavy Task Complete: Took {duration:.2f}s ---")
    print(resp.json())


async def main():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Fire the heavy task asynchronously
        heavy_task = asyncio.create_task(trigger_heavy_task(client))

        # 2. While that is running, spam the health check
        # If the API is blocked, these will hang until the heavy task finishes.
        # If the API is non-blocking (Multiprocessing), these will happen INSTANTLY.
        await asyncio.sleep(0.5)  # Give the heavy task a moment to hit the CPU

        for i in range(5):
            await check_health(client, i)
            await asyncio.sleep(0.5)

        await heavy_task


if __name__ == "__main__":
    print("Starting Stress Test...")
    asyncio.run(main())