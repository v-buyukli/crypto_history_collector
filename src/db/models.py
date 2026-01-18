from datetime import UTC, datetime

from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Exchange(Base):
    """Exchange model for storing supported cryptocurrency exchanges."""

    __tablename__ = "exchanges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    candles = relationship("Candle", back_populates="exchange")

    def __repr__(self):
        return f"<Exchange(id={self.id}, name={self.name})>"


class MarketType(Base):
    """Market type model for different trading markets (spot, futures, etc)."""

    __tablename__ = "market_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    candles = relationship("Candle", back_populates="market_type")

    def __repr__(self):
        return f"<MarketType(id={self.id}, name={self.name})>"


class Symbol(Base):
    """Symbol model for trading pairs (e.g., BTCUSDT, ETHUSDT)."""

    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    candles = relationship("Candle", back_populates="symbol")

    def __repr__(self):
        return f"<Symbol(id={self.id}, name={self.name})>"


class Candle(Base):
    """Candle/bar model for storing OHLCV data."""

    __tablename__ = "candles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    exchange_id = Column(Integer, ForeignKey("exchanges.id"), nullable=False)
    market_type_id = Column(Integer, ForeignKey("market_types.id"), nullable=False)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    timeframe = Column(String(10), nullable=False)
    timestamp = Column(DateTime, nullable=False)

    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    exchange = relationship("Exchange", back_populates="candles")
    market_type = relationship("MarketType", back_populates="candles")
    symbol = relationship("Symbol", back_populates="candles")

    def __repr__(self):
        symbol_name = self.symbol.name if self.symbol else None
        return f"<Candle(symbol={symbol_name}, timeframe={self.timeframe}, timestamp={self.timestamp})>"
