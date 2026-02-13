from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from app.enums import MarketTypeEnum, QuoteAssetEnum, TimeframeEnum


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

    @abstractmethod
    async def get_klines(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        start_time: datetime,
        end_time: datetime | None = None,
        market_type: MarketTypeEnum = MarketTypeEnum.SPOT,
    ) -> list[Kline]:
        """
        Fetch historical candles.

        Automatically paginates to retrieve the full date range.

        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            timeframe: Timeframe (e.g., "1h", "4h", "1d")
            start_time: Start of period
            end_time: End of period
            market_type: Market type ("spot" or "futures")

        Returns:
            List of candles
        """
        pass

    @staticmethod
    @abstractmethod
    async def get_active_symbols(
        market_type: MarketTypeEnum = MarketTypeEnum.FUTURES,
        quote_asset: QuoteAssetEnum = QuoteAssetEnum.USDT,
    ) -> list[str]:
        """
        Get list of active trading symbols.

        Args:
            market_type: Market type
            quote_asset: Quote asset filter

        Returns:
            List of active symbol names
        """
        pass
