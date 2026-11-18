"""Atomic request budgets and cooldowns for shared profile caches."""

import math
import threading
import time

from django.core.cache.backends.locmem import LocMemCache
from django.core.cache.backends.redis import RedisCache


class ProfileMemoryCache(LocMemCache):
    _budget_lock = threading.Lock()

    def take_token(self, key, capacity, refill_per_second):
        with self._budget_lock:
            now = time.time()
            tokens, updated_at = self.get(key, (capacity, now))
            tokens = min(capacity, tokens + max(0, now - updated_at) * refill_per_second)
            allowed = tokens >= 1
            self.set(key, (tokens - int(allowed), now),
                     timeout=math.ceil(capacity / refill_per_second))
            return allowed

    def extend_cooldown(self, key, seconds):
        with self._budget_lock:
            deadline = max(self.get(key, 0), time.time() + seconds)
            self.set(key, deadline, timeout=deadline - time.time())


class ProfileRedisCache(RedisCache):
    def take_token(self, key, capacity, refill_per_second):
        client = self._cache.get_client(write=True)
        return bool(client.eval(
            """
            local clock = redis.call('TIME')
            local now = tonumber(clock[1]) + tonumber(clock[2]) / 1000000
            local capacity = tonumber(ARGV[1])
            local refill = tonumber(ARGV[2])
            local previous = redis.call('HMGET', KEYS[1], 'tokens', 'updated_at')
            local tokens = tonumber(previous[1]) or capacity
            local updated_at = tonumber(previous[2]) or now
            tokens = math.min(capacity, tokens + math.max(0, now - updated_at) * refill)
            local allowed = 0
            if tokens >= 1 then
                tokens = tokens - 1
                allowed = 1
            end
            redis.call('HSET', KEYS[1], 'tokens', tokens, 'updated_at', now)
            redis.call('EXPIRE', KEYS[1], math.ceil(capacity / refill))
            return allowed
            """,
            1, self.make_and_validate_key(key), capacity, refill_per_second,
        ))

    def extend_cooldown(self, key, seconds):
        client = self._cache.get_client(write=True)
        client.eval(
            """
            local ttl = redis.call('TTL', KEYS[1])
            if ttl < tonumber(ARGV[1]) then
                redis.call('SET', KEYS[1], 1, 'EX', ARGV[1])
            end
            return 1
            """,
            1, self.make_and_validate_key(key), seconds,
        )
