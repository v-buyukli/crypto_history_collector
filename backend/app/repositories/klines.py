from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Candle, Exchange, ExchangeSymbol, MarketType, Symbol
from app.enums import ExchangeEnum, MarketTypeEnum, TimeframeEnum
from app.exchanges.base import Kline


class KlinesRepository:

    @staticmethod
    async def resolve_exchange_symbol_id(
        session: AsyncSession,
        exchange: ExchangeEnum,
        market_type: MarketTypeEnum,
        symbol_name: str,
    ) -> int | None:
        """Resolve exchange_symbol_id from exchange + market_type + symbol name.

        Returns the id if found and active, None otherwise.
        """
        stmt = (
            select(ExchangeSymbol.id)
            .join(Exchange, Exchange.id == ExchangeSymbol.exchange_id)
            .join(MarketType, MarketType.id == ExchangeSymbol.market_type_id)
            .join(Symbol, Symbol.id == ExchangeSymbol.symbol_id)
            .where(
                Exchange.name == exchange.value,
                MarketType.name == market_type.value,
                Symbol.name == symbol_name,
                ExchangeSymbol.is_active == True,  # noqa: E712
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def save_klines(
        session: AsyncSession,
        exchange_symbol_id: int,
        timeframe: TimeframeEnum,
        klines: list[Kline],
    ) -> int:
        """Bulk insert klines, skipping duplicates. Returns count of inserted rows."""
        if not klines:
            return 0

        rows = [
            {
                "exchange_symbol_id": exchange_symbol_id,
                "timeframe": timeframe.value,
                "timestamp": k.timestamp,
                "open": k.open,
                "high": k.high,
                "low": k.low,
                "close": k.close,
                "volume": k.volume,
            }
            for k in klines
        ]

        batch_size = 3000
        total_inserted = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            stmt = (
                insert(Candle)
                .values(batch)
                .on_conflict_do_nothing(constraint="uq_candle")
            )
            result = await session.execute(stmt)
            total_inserted += result.rowcount
        await session.commit()
        return total_inserted
