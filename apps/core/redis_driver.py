import aioredis
from core.config import settings


class RedisDriver:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        self.default_expire_time = 600

    async def connect(self):
        self.redis_client = await aioredis.create_redis_pool(self.redis_url)

    async def disconnect(self):
        self.redis_client.close()
        await self.redis_client.wait_closed()

    async def set_value(self, key: str, value: str, expire_time=None):
        """
        사용 편의를 위해 expire time default 값 설정
        """
        if expire_time is None:
            expire_time = self.default_expire_time
        await self.redis_client.set(key, value, expire=expire_time)


redis_driver = RedisDriver(redis_url=f"redis://{settings.REDIS_HOST}")
