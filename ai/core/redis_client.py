import os

import redis

from ai.core.commons import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB
from ai.core.utils import random_str


class RedisClient:
    redis_instance: redis.Redis

    def __init__(self):
        self.redis_instance = redis.Redis(host=REDIS_HOST,
                                          port=REDIS_PORT,
                                          password=REDIS_PASSWORD,
                                          db=REDIS_DB)

    def get_chat_data(self, chat_id):
        return self.redis_instance.hgetall(f"chat:{chat_id}")

    def set_chat_data(self, chat_id: int, data: str):
        self.redis_instance.hset(f"chat:{chat_id}", random_str(), data)

    def remove_chat_data(self, chat_id: int):
        self.redis_instance.delete(f"chat:{chat_id}")
