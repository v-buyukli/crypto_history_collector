from datetime import UTC, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
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

    exchange_symbols = relationship("ExchangeSymbol", back_populates="exchange")

    def __repr__(self):
        return f"<Exchange(id={self.id}, name={self.name})>"


class MarketType(Base):
    """Market type model for different trading markets (spot, futures)."""

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

    exchange_symbols = relationship("ExchangeSymbol", back_populates="market_type")

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

    exchange_symbols = relationship("ExchangeSymbol", back_populates="symbol")

    def __repr__(self):
        return f"<Symbol(id={self.id}, name={self.name})>"


class ExchangeSymbol(Base):
    """Link table between exchanges, market types, and symbols."""

    __tablename__ = "exchange_symbols"
    __table_args__ = (
        UniqueConstraint(
            "exchange_id", "market_type_id", "symbol_id", name="uq_exchange_symbol"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange_id = Column(Integer, ForeignKey("exchanges.id"), nullable=False)
    market_type_id = Column(Integer, ForeignKey("market_types.id"), nullable=False)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    exchange_symbol_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    exchange = relationship("Exchange", back_populates="exchange_symbols")
    market_type = relationship("MarketType", back_populates="exchange_symbols")
    symbol = relationship("Symbol", back_populates="exchange_symbols")
    candles = relationship("Candle", back_populates="exchange_symbol")

    def __repr__(self):
        return f"<ExchangeSymbol(id={self.id}, exchange_id={self.exchange_id}, symbol_id={self.symbol_id})>"


class Candle(Base):
    """Candle/bar model for storing OHLCV data."""

    __tablename__ = "candles"
    __table_args__ = (
        UniqueConstraint(
            "exchange_symbol_id", "timeframe", "timestamp", name="uq_candle"
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    exchange_symbol_id = Column(
        Integer, ForeignKey("exchange_symbols.id"), nullable=False
    )
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

    exchange_symbol = relationship("ExchangeSymbol", back_populates="candles")

    def __repr__(self):
        return f"<Candle(exchange_symbol_id={self.exchange_symbol_id}, timeframe={self.timeframe}, timestamp={self.timestamp})>"
