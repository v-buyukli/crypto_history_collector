"""Validate klines data integrity: detect gaps and duplicates.

Edit the configuration below, then run:
    python -m app.scripts.validate_klines
"""

import asyncio
from datetime import timedelta

from sqlalchemy import func, select

from app.db.models import Candle, Exchange, ExchangeSymbol, MarketType, Symbol
from app.db.session import AsyncSessionLocal
from app.enums import ExchangeEnum, MarketTypeEnum, TimeframeEnum


# ── Configuration ──────────────────────────────────────────────
EXCHANGE = ExchangeEnum.BINANCE
MARKET_TYPE = MarketTypeEnum.FUTURES
TIMEFRAME = TimeframeEnum.h1
# ───────────────────────────────────────────────────────────────

TIMEFRAME_DELTA = {
    TimeframeEnum.h1: timedelta(hours=1),
    TimeframeEnum.h4: timedelta(hours=4),
    TimeframeEnum.d1: timedelta(days=1),
}


async def main() -> None:
    expected_step = TIMEFRAME_DELTA[TIMEFRAME]

    symbols_checked = 0
    symbols_with_issues = 0

    async with AsyncSessionLocal() as session:
        # Get all active exchange symbols for the configured exchange + market type
        query = (
            select(ExchangeSymbol.id, Symbol.name)
            .join(Exchange, ExchangeSymbol.exchange_id == Exchange.id)
            .join(MarketType, ExchangeSymbol.market_type_id == MarketType.id)
            .join(Symbol, ExchangeSymbol.symbol_id == Symbol.id)
            .where(
                Exchange.name == EXCHANGE.value,
                MarketType.name == MARKET_TYPE.value,
                ExchangeSymbol.is_active.is_(True),
            )
            .order_by(Symbol.name)
        )
        result = await session.execute(query)
        exchange_symbols = result.all()

        for es_id, symbol_name in exchange_symbols:
            symbols_checked += 1

            # Check duplicates
            dup_query = (
                select(Candle.timestamp, func.count().label("cnt"))
                .where(
                    Candle.exchange_symbol_id == es_id,
                    Candle.timeframe == TIMEFRAME.value,
                )
                .group_by(Candle.timestamp)
                .having(func.count() > 1)
            )
            dup_result = await session.execute(dup_query)
            duplicates = dup_result.all()

            # Get sorted timestamps for gap detection
            ts_query = (
                select(Candle.timestamp)
                .where(
                    Candle.exchange_symbol_id == es_id,
                    Candle.timeframe == TIMEFRAME.value,
                )
                .order_by(Candle.timestamp)
            )
            ts_result = await session.execute(ts_query)
            timestamps = [row[0] for row in ts_result.all()]

            # Detect gaps
            gaps = []
            for i in range(1, len(timestamps)):
                diff = timestamps[i] - timestamps[i - 1]
                if diff != expected_step:
                    gaps.append((timestamps[i - 1], timestamps[i], diff))

            if duplicates or gaps:
                symbols_with_issues += 1
                print(
                    f"{symbol_name}: {len(timestamps)} candles, "
                    f"{len(gaps)} gaps, {len(duplicates)} duplicates"
                )
                for prev_ts, next_ts, diff in gaps[:5]:
                    print(f"  gap: {prev_ts} -> {next_ts} (delta={diff})")
                if len(gaps) > 5:
                    print(f"  ... and {len(gaps) - 5} more gaps")
                for ts, cnt in duplicates[:5]:
                    print(f"  duplicate: {ts} (count={cnt})")

    print("─" * 40)
    print(
        f"Done. Checked {symbols_checked} symbols, "
        f"{symbols_with_issues} with issues."
    )


if __name__ == "__main__":
    asyncio.run(main())
