import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime

import httpx

from app.enums import MarketTypeEnum, QuoteAssetEnum, TimeframeEnum


logger = logging.getLogger(__name__)


@dataclass
class Kline:
    """Standardized candle structure."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class RateLimiter:
    """Token-bucket rate limiter for async HTTP requests."""

    def __init__(self, rate: float):
        """
        Args:
            rate: Maximum requests per second.
        """
        self._interval = 1.0 / rate
        self._semaphore = asyncio.Semaphore(1)
        self._last_request: float = 0.0

    async def acquire(self) -> None:
        async with self._semaphore:
            now = time.monotonic()
            wait = self._last_request + self._interval - now
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request = time.monotonic()


class BaseExchangeClient(ABC):
    """Abstract base exchange client."""

    RATE_LIMIT: float = 10.0  # requests per second, override in subclasses
    MAX_RETRIES: int = 3
    RETRY_STATUSES: set[int] = {429, 500, 502, 503, 504}

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self._external_client = http_client
        self._rate_limiter = RateLimiter(self.RATE_LIMIT)

    async def _request_with_retry(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: dict,
    ) -> httpx.Response:
        """Execute GET request with rate limiting and exponential backoff retry."""
        for attempt in range(self.MAX_RETRIES):
            await self._rate_limiter.acquire()
            try:
                response = await client.get(url, params=params)
                if response.status_code not in self.RETRY_STATUSES:
                    response.raise_for_status()
                    return response

                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    delay = float(retry_after)
                else:
                    delay = 2**attempt

                logger.warning(
                    "HTTP %d for %s, retry %d/%d in %.1fs",
                    response.status_code,
                    url,
                    attempt + 1,
                    self.MAX_RETRIES,
                    delay,
                )
                await asyncio.sleep(delay)

            except httpx.TransportError as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise
                delay = 2**attempt
                logger.warning(
                    "Transport error for %s: %s, retry %d/%d in %.1fs",
                    url,
                    e,
                    attempt + 1,
                    self.MAX_RETRIES,
                    delay,
                )
                await asyncio.sleep(delay)

        # Final attempt without catching
        await self._rate_limiter.acquire()
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response

    @abstractmethod
    async def get_klines(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        start_time: datetime,
        end_time: datetime | None = None,
        market_type: MarketTypeEnum = MarketTypeEnum.SPOT,
    ) -> AsyncGenerator[list[Kline], None]:
        """
        Fetch historical candles, yielding batches as they arrive.

        Each yield is a list of Kline objects from one API page.
        """
        yield  # pragma: no cover
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    @abstractmethod
    async def get_active_symbols(
        market_type: MarketTypeEnum = MarketTypeEnum.FUTURES,
        quote_asset: QuoteAssetEnum = QuoteAssetEnum.USDT,
    ) -> list[str]:
        """Get list of active trading symbols."""
        pass
