import redis
import hashlib
import json
from core.config import settings


class RedisDriver:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        self.default_expire_time = 600

    def generate_cache_key(self, *args, **kwargs) -> str:
        """
        주어진 파라미터들로부터 유니크한 캐시 키를 생성합니다. 파라미터들은 해시 함수를 통해 처리됩니다.
        """
        # args와 kwargs를 정렬된 상태로 문자열로 변환
        key_base = json.dumps(
            {"args": args, "kwargs": sorted(kwargs.items())}, sort_keys=True
        )
        # MD5 해시 함수를 사용하여 유니크한 키 생성
        key_hash = hashlib.md5(key_base.encode()).hexdigest()
        return f"cache:{key_hash}"

    def connect(self):
        self.redis_client = redis.Redis.from_url(self.redis_url)

    def set_value(self, key: str, value: str, expire_time=None):
        """
        사용 편의를 위해 expire time default 값 설정
        """
        if expire_time is None:
            expire_time = self.default_expire_time
        self.redis_client.set(key, value, ex=expire_time)

    def get_value(self, key: str):
        """
        주어진 키에 대한 값을 Redis에서 조회합니다.
        """
        value = self.redis_client.get(key)
        return json.loads(value)

    def is_cached(self, key: str) -> bool:
        """
        주어진 키가 Redis에 존재하는지 확인합니다.
        """
        return self.redis_client.exists(key) > 0


redis_driver = RedisDriver(redis_url=f"redis://{settings.REDIS_HOST}")
