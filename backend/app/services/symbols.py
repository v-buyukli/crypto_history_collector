from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.symbols import SymbolsRepository
from app.schemas.symbols import SymbolsRequest, SymbolsResponse, UpdateSymbolsResponse
from app.services.mappers import EXCHANGE_CLIENTS


class SymbolsService:

    @staticmethod
    async def get_active(
        session: AsyncSession,
        symbols_request: SymbolsRequest,
    ) -> SymbolsResponse:
        try:
            symbols = await SymbolsRepository.get_active_symbols(
                session=session,
                exchange=symbols_request.exchange,
                market_type=symbols_request.market_type,
                quote_asset=symbols_request.quote_asset,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch symbols: {e}",
            )

        return SymbolsResponse(
            exchange=symbols_request.exchange,
            market_type=symbols_request.market_type,
            quote_asset=symbols_request.quote_asset,
            symbols=symbols,
            count=len(symbols),
        )

    @staticmethod
    async def update(
        session: AsyncSession,
        symbols_request: SymbolsRequest,
    ) -> UpdateSymbolsResponse:
        client_class = EXCHANGE_CLIENTS[symbols_request.exchange]

        try:
            current_symbols = await client_class.get_active_symbols(
                market_type=symbols_request.market_type,
                quote_asset=symbols_request.quote_asset,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch symbols from exchange: {e}",
            )

        try:
            stats = await SymbolsRepository.update_symbols(
                session=session,
                exchange=symbols_request.exchange,
                market_type=symbols_request.market_type,
                current_symbols=current_symbols,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update symbols in database: {e}",
            )

        return UpdateSymbolsResponse(
            exchange=symbols_request.exchange,
            market_type=symbols_request.market_type,
            quote_asset=symbols_request.quote_asset,
            **stats,
        )
