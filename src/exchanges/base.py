from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Kline:
    """Standardized candle structure."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class BaseExchangeClient(ABC):
    """Abstract base exchange client."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Exchange name."""
        pass

    @abstractmethod
    async def get_klines(
        self,
        symbol: str,
        timeframe: str,
        market_type: str = "spot",
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 1000,
    ) -> list[Kline]:
        """
        Fetch historical candles.

        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            timeframe: Timeframe (e.g., "1h", "4h", "1d")
            market_type: Market type ("spot" or "futures")
            start_time: Start of period
            end_time: End of period
            limit: Maximum number of candles

        Returns:
            List of candles
        """
        pass

    @abstractmethod
    def get_supported_timeframes(self) -> list[str]:
        """List of supported timeframes."""
        pass

    @abstractmethod
    def get_supported_market_types(self) -> list[str]:
        """List of supported market types."""
        pass
