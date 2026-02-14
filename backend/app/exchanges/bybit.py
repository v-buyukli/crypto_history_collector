from collections.abc import AsyncGenerator
from datetime import datetime

import httpx

from app.enums import MarketTypeEnum, QuoteAssetEnum, TimeframeEnum
from app.exchanges.base import BaseExchangeClient, Kline


BYBIT_BASE_URL = "https://api.bybit.com"

BYBIT_CATEGORY_MAP: dict[MarketTypeEnum, str] = {
    MarketTypeEnum.SPOT: "spot",
    MarketTypeEnum.FUTURES: "linear",
}

BYBIT_TIMEFRAME_MAP: dict[TimeframeEnum, str] = {
    TimeframeEnum.h1: "60",
    TimeframeEnum.h4: "240",
    TimeframeEnum.d1: "D",
}


class BybitClient(BaseExchangeClient):
    """Bybit V5 public API client (spot + linear futures)."""

    RATE_LIMIT: float = 10.0

    @staticmethod
    async def get_active_symbols(
        market_type: MarketTypeEnum = MarketTypeEnum.FUTURES,
        quote_asset: QuoteAssetEnum = QuoteAssetEnum.USDT,
    ) -> list[str]:
        category = BYBIT_CATEGORY_MAP[market_type]
        url = f"{BYBIT_BASE_URL}/v5/market/instruments-info"
        symbols: list[str] = []

        async with httpx.AsyncClient(timeout=30) as client:
            cursor: str | None = None
            while True:
                params: dict = {
                    "category": category,
                    "limit": "1000",
                    "status": "Trading",
                }
                if cursor:
                    params["cursor"] = cursor

                response = await client.get(url, params=params)
                response.raise_for_status()
                body = response.json()

                if body.get("retCode") != 0:
                    raise RuntimeError(f"Bybit API error: {body.get('retMsg')}")

                result = body["result"]
                for item in result["list"]:
                    sym = item["symbol"]
                    if sym.endswith(quote_asset.value.upper()):
                        symbols.append(sym)

                cursor = result.get("nextPageCursor")
                if not cursor:
                    break

        return symbols

    _PAGE_LIMIT = 1000

    async def get_klines(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        start_time: datetime,
        end_time: datetime | None = None,
        market_type: MarketTypeEnum = MarketTypeEnum.SPOT,
    ) -> AsyncGenerator[list[Kline], None]:
        category = BYBIT_CATEGORY_MAP[market_type]
        interval = BYBIT_TIMEFRAME_MAP[timeframe]
        url = f"{BYBIT_BASE_URL}/v5/market/kline"

        start_ms = int(start_time.timestamp() * 1000)
        current_end_ms = int(end_time.timestamp() * 1000) if end_time else None

        params: dict = {
            "category": category,
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": self._PAGE_LIMIT,
            "start": start_ms,
        }

        own_client = self._external_client is None
        client = self._external_client or httpx.AsyncClient(timeout=30)

        try:
            while True:
                if current_end_ms is not None:
                    params["end"] = current_end_ms

                data = await self._fetch_klines_page(client, url, params)
                if not data:
                    break

                yield self._parse_klines(data)

                if len(data) < self._PAGE_LIMIT:
                    break

                # Bybit returns newest first: data[0]=newest, data[-1]=oldest.
                # Paginate backwards by moving end before the oldest candle.
                oldest_open_time_ms = int(data[-1][0])
                current_end_ms = oldest_open_time_ms - 1
                if current_end_ms <= start_ms:
                    break
        finally:
            if own_client:
                await client.aclose()

    async def _fetch_klines_page(
        self, client: httpx.AsyncClient, url: str, params: dict
    ) -> list:
        response = await self._request_with_retry(client, url, params)
        body = response.json()

        if body.get("retCode") != 0:
            raise RuntimeError(f"Bybit API error: {body.get('retMsg')}")

        return body["result"]["list"]

    def _parse_klines(self, data: list) -> list[Kline]:
        """
        Parse Bybit V5 kline response into list of Kline.

        Bybit format (newest first):
        [
            ["1670608800000", "17071", "17073", "17027", "17055.5", "268.276"],
            ...
        ]

        Fields: [startTime, openPrice, highPrice, lowPrice, closePrice, volume, ...]
        """
        klines = []
        for item in reversed(data):
            kline = Kline(
                timestamp=datetime.fromtimestamp(int(item[0]) / 1000),
                open=float(item[1]),
                high=float(item[2]),
                low=float(item[3]),
                close=float(item[4]),
                volume=float(item[5]),
            )
            klines.append(kline)
        return klines
