import os
import redis.asyncio as redis
from typing import Optional

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisClient:
    _instance = None

    def __init__(self):
        # Create connection pool
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)

    @classmethod
    def get_instance(cls):
        # Singleton pattern for the connection pool
        if cls._instance is None:
            cls._instance = RedisClient()
        return cls._instance

    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 10):
        # TTL = Time To Live (Expire in 10 seconds)
        await self.redis.set(key, value, ex=ttl)

    async def close(self):
        await self.redis.close()