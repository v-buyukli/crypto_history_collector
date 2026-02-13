"""Backfill klines for a list of symbols.

Edit the configuration below, then run:
    python -m app.scripts.backfill_klines
"""

import asyncio
from datetime import datetime

from app.db.session import AsyncSessionLocal
from app.enums import ExchangeEnum, MarketTypeEnum, TimeframeEnum
from app.mappers import EXCHANGE_CLIENTS
from app.repositories.klines import KlinesRepository


# ── Configuration ──────────────────────────────────────────────
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
TIMEFRAME = TimeframeEnum.h1
START_TIME = datetime(2019, 1, 1)
END_TIME = datetime(2026, 2, 10)  # None = up to now
EXCHANGE = ExchangeEnum.BINANCE
MARKET_TYPE = MarketTypeEnum.FUTURES
# ───────────────────────────────────────────────────────────────


async def main() -> None:
    client = EXCHANGE_CLIENTS[EXCHANGE]()

    total_fetched = 0
    total_inserted = 0
    skipped: list[str] = []

    async with AsyncSessionLocal() as session:
        for symbol in SYMBOLS:
            exchange_symbol_id = await KlinesRepository.resolve_exchange_symbol_id(
                session,
                EXCHANGE,
                MARKET_TYPE,
                symbol,
            )
            if exchange_symbol_id is None:
                print(
                    f"WARNING: {symbol} not found for {EXCHANGE.value}/{MARKET_TYPE.value}, skipping"
                )
                skipped.append(symbol)
                continue

            klines = await client.get_klines(
                symbol=symbol,
                timeframe=TIMEFRAME,
                start_time=START_TIME,
                end_time=END_TIME,
                market_type=MARKET_TYPE,
            )

            inserted = await KlinesRepository.save_klines(
                session,
                exchange_symbol_id,
                TIMEFRAME,
                klines,
            )

            total_fetched += len(klines)
            total_inserted += inserted
            print(f"{symbol}: fetched {len(klines)}, inserted {inserted}")

    print("─" * 40)
    print(f"Done. Fetched {total_fetched}, inserted {total_inserted}")
    if skipped:
        print(f"Skipped symbols: {', '.join(skipped)}")


if __name__ == "__main__":
    asyncio.run(main())
