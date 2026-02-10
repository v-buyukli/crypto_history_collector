from datetime import datetime

import httpx

from app.enums import MarketTypeEnum, QuoteAssetEnum, TimeframeEnum
from app.exchanges.base import BaseExchangeClient, Kline


BINANCE_BASE_URLS: dict[MarketTypeEnum, str] = {
    MarketTypeEnum.SPOT: "https://api.binance.com",
    MarketTypeEnum.FUTURES: "https://fapi.binance.com",
}

BINANCE_KLINE_ENDPOINTS: dict[MarketTypeEnum, str] = {
    MarketTypeEnum.SPOT: "/api/v3/klines",
    MarketTypeEnum.FUTURES: "/fapi/v1/klines",
}

BINANCE_EXCHANGE_INFO_ENDPOINTS: dict[MarketTypeEnum, str] = {
    MarketTypeEnum.SPOT: "/api/v3/exchangeInfo",
    MarketTypeEnum.FUTURES: "/fapi/v1/exchangeInfo",
}


class BinanceClient(BaseExchangeClient):
    """Binance public API client (spot + futures)."""

    @staticmethod
    async def get_active_symbols(
        market_type: MarketTypeEnum = MarketTypeEnum.FUTURES,
        quote_asset: QuoteAssetEnum = QuoteAssetEnum.USDT,
    ) -> list[str]:
        """
        Get list of active trading symbols.

        Args:
            market_type: "spot" or "futures"
            quote_asset: Quote asset filter (e.g., "USDT")

        Returns:
            List of active symbol names
        """
        base_url = BINANCE_BASE_URLS[market_type]
        endpoint = BINANCE_EXCHANGE_INFO_ENDPOINTS[market_type]
        url = f"{base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            exchange_info = response.json()

        return [
            item["symbol"]
            for item in exchange_info["symbols"]
            if item["symbol"].endswith(quote_asset.value.upper())
            and item["status"] == "TRADING"
        ]

    async def get_klines(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        market_type: MarketTypeEnum = MarketTypeEnum.SPOT,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 1000,
    ) -> list[Kline]:
        """
        Fetch historical candles from Binance.

        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            timeframe: Timeframe (e.g., "1h", "4h", "1d")
            market_type: Market type ("spot" or "futures")
            start_time: Start of period
            end_time: End of period
            limit: Maximum number of candles (max 1000)

        Returns:
            List of candles
        """
        if market_type not in MarketTypeEnum:
            raise ValueError(f"Unsupported market type: {market_type}")

        if timeframe not in TimeframeEnum:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        limit = min(limit, 1000)

        base_url = BINANCE_BASE_URLS[market_type]
        endpoint = BINANCE_KLINE_ENDPOINTS[market_type]

        params: dict = {
            "symbol": symbol.upper(),
            "interval": timeframe,
            "limit": limit,
        }

        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            params["endTime"] = int(end_time.timestamp() * 1000)

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}{endpoint}", params=params)
            response.raise_for_status()
            data = response.json()

        return self._parse_klines(data)

    def _parse_klines(self, data: list) -> list[Kline]:
        """
        Parse Binance API response into list of Kline.

        Binance format:
        [
            [
                1499040000000,      // Open time (ms)
                "0.01634000",       // Open
                "0.80000000",       // High
                "0.01575800",       // Low
                "0.01577100",       // Close
                "148976.11427815",  // Volume
                ...
            ],
            ...
        ]
        """
        klines = []
        for item in data:
            kline = Kline(
                timestamp=datetime.fromtimestamp(item[0] / 1000),
                open=float(item[1]),
                high=float(item[2]),
                low=float(item[3]),
                close=float(item[4]),
                volume=float(item[5]),
            )
            klines.append(kline)
        return klines
