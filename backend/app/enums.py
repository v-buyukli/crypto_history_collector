from enum import StrEnum


class ExchangeEnum(StrEnum):
    """Supported exchanges."""

    BINANCE = "binance"


class MarketTypeEnum(StrEnum):
    """Supported market types."""

    SPOT = "spot"
    FUTURES = "futures"


class QuoteAssetEnum(StrEnum):
    """Supported quote assets."""

    USDT = "usdt"


class TimeframeEnum(StrEnum):
    """Supported timeframes."""

    h1 = "1h"
    h4 = "4h"
    d1 = "1d"
