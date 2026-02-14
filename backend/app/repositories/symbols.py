from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db import Exchange, ExchangeSymbol, MarketType, Symbol
from app.enums import ExchangeEnum, MarketTypeEnum, QuoteAssetEnum


class SymbolsRepository:
    """Repository for fetching trading symbols from database."""

    @staticmethod
    async def update_symbols(
        session: AsyncSession,
        exchange: ExchangeEnum,
        market_type: MarketTypeEnum,
        current_symbols: list[str],
    ) -> dict:
        """
        Update symbols in database: add new, reactivate returned, deactivate missing.

        Returns:
            Dict with update statistics (added, activated, deactivated, total_active)
        """
        result = await session.execute(
            select(Exchange).where(Exchange.name == exchange.value)
        )
        exchange_db = result.scalars().one()

        result = await session.execute(
            select(MarketType).where(MarketType.name == market_type.value)
        )
        market_type_db = result.scalars().one()

        result = await session.execute(
            select(ExchangeSymbol)
            .options(joinedload(ExchangeSymbol.symbol))
            .where(
                ExchangeSymbol.exchange_id == exchange_db.id,
                ExchangeSymbol.market_type_id == market_type_db.id,
            )
        )
        existing_exchange_symbols = result.scalars().unique().all()

        existing_by_name: dict[str, ExchangeSymbol] = {
            es.symbol.name: es for es in existing_exchange_symbols
        }

        added = 0
        activated = 0
        deactivated = 0
        current_symbols_set = set(current_symbols)

        # add new or reactivate
        for symbol_name in current_symbols:
            if symbol_name in existing_by_name:
                es = existing_by_name[symbol_name]
                if not es.is_active:
                    es.is_active = True
                    activated += 1
            else:
                # get or create Symbol
                result = await session.execute(
                    select(Symbol).where(Symbol.name == symbol_name)
                )
                symbol = result.scalars().first()
                if not symbol:
                    symbol = Symbol(name=symbol_name)
                    session.add(symbol)
                    await session.flush()

                exchange_symbol = ExchangeSymbol(
                    exchange_id=exchange_db.id,
                    market_type_id=market_type_db.id,
                    symbol_id=symbol.id,
                    exchange_symbol_name=symbol_name,
                    is_active=True,
                )
                session.add(exchange_symbol)
                added += 1

        # deactivate missing
        for symbol_name, es in existing_by_name.items():
            if symbol_name not in current_symbols_set and es.is_active:
                es.is_active = False
                deactivated += 1

        await session.commit()

        return {
            "total_active": len(current_symbols),
            "added": added,
            "activated": activated,
            "deactivated": deactivated,
        }

    @staticmethod
    async def get_active_symbols(
        session: AsyncSession,
        exchange: ExchangeEnum,
        market_type: MarketTypeEnum = MarketTypeEnum.FUTURES,
        quote_asset: QuoteAssetEnum = QuoteAssetEnum.USDT,
    ) -> list[str]:
        """
        Get list of active trading symbols from database.

        Args:
            session: Async database session
            exchange: Exchange enum
            market_type: Market type enum
            quote_asset: Quote asset enum

        Returns:
            List of active symbol names
        """
        stmt = (
            select(Symbol.name)
            .join(ExchangeSymbol, ExchangeSymbol.symbol_id == Symbol.id)
            .join(Exchange, Exchange.id == ExchangeSymbol.exchange_id)
            .join(MarketType, MarketType.id == ExchangeSymbol.market_type_id)
            .where(
                Exchange.name == exchange.value,
                MarketType.name == market_type.value,
                ExchangeSymbol.is_active == True,  # noqa: E712
                Symbol.name.endswith(quote_asset.value.upper()),
            )
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())
