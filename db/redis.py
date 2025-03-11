import redis.asyncio as aioredis
from config import REDIS_URL

class Redis:
    def __init__(self):
        self.redis = None

    async def create_connection(self):
        self.redis = await aioredis.from_url(REDIS_URL)
        
    async def close(self):
        if self.redis:
            await self.redis.close()

redis = Redis()
