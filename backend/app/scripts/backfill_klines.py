"""Backfill klines for a list of symbols.

Edit the configuration below, then run:
    python -m app.scripts.backfill_klines
"""

import asyncio
import logging
from datetime import datetime

import httpx

from app.db.session import AsyncSessionLocal
from app.enums import ExchangeEnum, MarketTypeEnum, TimeframeEnum
from app.repositories.klines import KlinesRepository
from app.services.mappers import EXCHANGE_CLIENTS


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Configuration ──────────────────────────────────────────────
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
TIMEFRAME = TimeframeEnum.h1
START_TIME = datetime(2020, 1, 1)
END_TIME = datetime(2026, 2, 10)  # None = up to now
EXCHANGE = ExchangeEnum.BYBIT
MARKET_TYPE = MarketTypeEnum.FUTURES
MAX_CONCURRENT = 5  # parallel symbols
# ───────────────────────────────────────────────────────────────


async def backfill_symbol(
    client,
    symbol: str,
    idx: int,
    total: int,
    semaphore: asyncio.Semaphore,
) -> tuple[str, int, int]:
    """Backfill one symbol. Returns (symbol, fetched, inserted)."""
    async with semaphore:
        async with AsyncSessionLocal() as session:
            exchange_symbol_id = await KlinesRepository.resolve_exchange_symbol_id(
                session,
                EXCHANGE,
                MARKET_TYPE,
                symbol,
            )

            if exchange_symbol_id is None:
                logger.warning(
                    "[%d/%d] %s not found for %s/%s, skipping",
                    idx,
                    total,
                    symbol,
                    EXCHANGE.value,
                    MARKET_TYPE.value,
                )
                return symbol, 0, -1  # -1 = skipped

            fetched = 0
            inserted = 0

            async for batch in client.get_klines(
                symbol=symbol,
                timeframe=TIMEFRAME,
                start_time=START_TIME,
                end_time=END_TIME,
                market_type=MARKET_TYPE,
            ):
                batch_inserted = await KlinesRepository.save_klines(
                    session,
                    exchange_symbol_id,
                    TIMEFRAME,
                    batch,
                )
                fetched += len(batch)
                inserted += batch_inserted

            logger.info(
                "[%d/%d] %s: fetched %d, inserted %d",
                idx,
                total,
                symbol,
                fetched,
                inserted,
            )

            return symbol, fetched, inserted


async def main() -> None:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async with httpx.AsyncClient(timeout=30) as http_client:
        client = EXCHANGE_CLIENTS[EXCHANGE](http_client=http_client)

        tasks = [
            backfill_symbol(client, symbol, idx, len(SYMBOLS), semaphore)
            for idx, symbol in enumerate(SYMBOLS, start=1)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

    total_fetched = 0
    total_inserted = 0
    skipped: list[str] = []
    errors: list[str] = []

    for result in results:
        if isinstance(result, Exception):
            errors.append(str(result))
            continue

        symbol, fetched, inserted = result
        if inserted == -1:
            skipped.append(symbol)
            continue
        total_fetched += fetched
        total_inserted += inserted

    logger.info("─" * 40)
    logger.info("Done. Fetched %d, inserted %d", total_fetched, total_inserted)
    if skipped:
        logger.info("Skipped symbols: %s", ", ".join(skipped))
    if errors:
        logger.error("Errors: %s", "\n".join(errors))


if __name__ == "__main__":
    asyncio.run(main())
