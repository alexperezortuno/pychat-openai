import os

import redis

from ai.core.utils import random_str


class RedisClient:
    redis_instance: redis.Redis

    def __init__(self):
        self.redis_instance = redis.Redis(host=os.getenv("REDIS_HOST", 'redis'),
                                          port=os.getenv("REDIS_PORT", 6379),
                                          password=os.getenv("REDIS_PASSWORD", None),
                                          db=os.getenv("REDIS_DB", 0))

    def get_chat_data(self, chat_id):
        return self.redis_instance.hgetall(f"chat:{chat_id}")

    def set_chat_data(self, chat_id: int, data: str):
        self.redis_instance.hset(f"chat:{chat_id}", random_str(), data)

    def remove_chat_data(self, chat_id: int):
        self.redis_instance.delete(f"chat:{chat_id}")
