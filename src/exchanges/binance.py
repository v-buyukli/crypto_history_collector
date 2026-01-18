from datetime import datetime

import httpx

from src.exchanges.base import BaseExchangeClient, Kline


class BinanceClient(BaseExchangeClient):
    """Binance public API client (spot + futures)."""

    BASE_URL_SPOT = "https://api.binance.com"
    BASE_URL_FUTURES = "https://fapi.binance.com"

    SUPPORTED_TIMEFRAMES = [
        "1h",
        "4h",
        "1d",
    ]

    SUPPORTED_MARKET_TYPES = ["spot", "futures"]

    @property
    def name(self) -> str:
        return "binance"

    def get_supported_timeframes(self) -> list[str]:
        return self.SUPPORTED_TIMEFRAMES

    def get_supported_market_types(self) -> list[str]:
        return self.SUPPORTED_MARKET_TYPES

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
        if market_type not in self.SUPPORTED_MARKET_TYPES:
            raise ValueError(f"Unsupported market type: {market_type}")

        if timeframe not in self.SUPPORTED_TIMEFRAMES:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        limit = min(limit, 1000)

        base_url = (
            self.BASE_URL_SPOT if market_type == "spot" else self.BASE_URL_FUTURES
        )
        endpoint = "/api/v3/klines" if market_type == "spot" else "/fapi/v1/klines"

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
