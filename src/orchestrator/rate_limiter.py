"""Token-bucket rate limiter for provider calls."""

import asyncio
import time
from dataclasses import dataclass, field

from config.settings import settings
from src.utils.rate_utils import per_minute_to_per_second


@dataclass
class TokenBucket:
    capacity: int
    refill_rate: float
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        self.tokens = float(self.capacity)

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def try_acquire(self, tokens: int = 1) -> bool:
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    async def wait_and_acquire(self, tokens: int = 1) -> None:
        while not self.try_acquire(tokens):
            wait_time = (tokens - self.tokens) / max(self.refill_rate, 0.001)
            await asyncio.sleep(min(wait_time, 1.0))


class RateLimiter:
    def __init__(self):
        self.buckets = {
            "groq": TokenBucket(settings.groq_requests_per_minute, per_minute_to_per_second(settings.groq_requests_per_minute)),
            "cerebras": TokenBucket(60, 1.0),
            "gemini": TokenBucket(15, 0.25),
            "ollama": TokenBucket(1000, 100.0),
        }
        self.daily_counts = {"groq": 0, "cerebras": 0, "gemini": 0}
        self.daily_reset_date = time.strftime("%Y-%m-%d")

    async def acquire(self, provider: str) -> None:
        if not settings.rate_limit_enabled:
            return
        self._check_daily_reset()
        bucket = self.buckets.get(provider)
        if bucket:
            await bucket.wait_and_acquire()
        self.daily_counts[provider] = self.daily_counts.get(provider, 0) + 1

    def can_use(self, provider: str) -> bool:
        self._check_daily_reset()
        limits = {"groq": 14400, "cerebras": 10000, "gemini": 1500}
        return self.daily_counts.get(provider, 0) < limits.get(provider, float("inf"))

    def status(self) -> dict:
        return {
            provider: {"requests_today": self.daily_counts.get(provider, 0), "bucket_tokens": int(bucket.tokens)}
            for provider, bucket in self.buckets.items()
        }

    def _check_daily_reset(self) -> None:
        today = time.strftime("%Y-%m-%d")
        if today != self.daily_reset_date:
            self.daily_counts = {key: 0 for key in self.daily_counts}
            self.daily_reset_date = today
