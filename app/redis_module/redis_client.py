import aioredis
from config.settings import settings

redis = aioredis.from_url(f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}", decode_responses=True)
