import aioredis


class RedisDriver:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None

    async def connect(self):
        self.redis_client = await aioredis.create_redis_pool(self.redis_url)

    async def disconnect(self):
        self.redis_client.close()
        await self.redis_client.wait_closed()
