"""Export klines from DB to CSV files (one file per ticker).

Edit the configuration below, then run:
    python -m app.scripts.export_klines_csv
"""

import asyncio
import csv
from pathlib import Path

from sqlalchemy import select

from app.db.models import Candle, Exchange, ExchangeSymbol, MarketType, Symbol
from app.db.session import AsyncSessionLocal
from app.enums import ExchangeEnum, MarketTypeEnum, TimeframeEnum


# ── Configuration ──────────────────────────────────────────────
EXCHANGE = ExchangeEnum.BYBIT
MARKET_TYPE = MarketTypeEnum.FUTURES
TIMEFRAME = TimeframeEnum.h1
OUTPUT_DIR = Path("exported_klines")
# ───────────────────────────────────────────────────────────────


async def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_symbols = 0
    total_candles = 0
    failed_symbols: list[str] = []

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
            try:
                # Query candles ordered by timestamp
                candle_query = (
                    select(
                        Candle.timestamp,
                        Candle.open,
                        Candle.high,
                        Candle.low,
                        Candle.close,
                        Candle.volume,
                    )
                    .where(
                        Candle.exchange_symbol_id == es_id,
                        Candle.timeframe == TIMEFRAME.value,
                    )
                    .order_by(Candle.timestamp)
                )
                candle_result = await session.execute(candle_query)
                candles = candle_result.all()

                if not candles:
                    continue

                # Write CSV
                filepath = OUTPUT_DIR / f"{symbol_name}.csv"
                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]
                    )
                    for ts, open_, high, low, close, volume in candles:
                        writer.writerow(
                            [
                                ts.strftime("%Y-%m-%d %H:%M:%S"),
                                symbol_name,
                                open_,
                                high,
                                low,
                                close,
                                volume,
                            ]
                        )

                total_symbols += 1
                total_candles += len(candles)
                print(f"{symbol_name}: {len(candles)} candles -> {filepath}")
            except Exception as e:
                failed_symbols.append(f"{symbol_name} ({e})")
                print(f"SKIP {symbol_name}: {e}")

    print("─" * 40)
    print(f"Done. Exported {total_candles} candles for {total_symbols} symbols.")
    if failed_symbols:
        print(f"\nFailed ({len(failed_symbols)}):")
        for s in failed_symbols:
            print(f"  - {s}")


if __name__ == "__main__":
    asyncio.run(main())
