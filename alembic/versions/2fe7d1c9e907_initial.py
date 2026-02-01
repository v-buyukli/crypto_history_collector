"""initial

Revision ID: 2fe7d1c9e907
Revises:
Create Date: 2026-01-31

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "2fe7d1c9e907"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create exchanges table
    op.create_table(
        "exchanges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Create market_types table
    op.create_table(
        "market_types",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Create symbols table
    op.create_table(
        "symbols",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Create exchange_symbols table
    op.create_table(
        "exchange_symbols",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("exchange_id", sa.Integer(), nullable=False),
        sa.Column("market_type_id", sa.Integer(), nullable=False),
        sa.Column("symbol_id", sa.Integer(), nullable=False),
        sa.Column("exchange_symbol_name", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["exchange_id"], ["exchanges.id"]),
        sa.ForeignKeyConstraint(["market_type_id"], ["market_types.id"]),
        sa.ForeignKeyConstraint(["symbol_id"], ["symbols.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "exchange_id", "market_type_id", "symbol_id", name="uq_exchange_symbol"
        ),
    )

    # Create candles table
    op.create_table(
        "candles",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("exchange_symbol_id", sa.Integer(), nullable=False),
        sa.Column("timeframe", sa.String(length=10), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["exchange_symbol_id"], ["exchange_symbols.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "exchange_symbol_id", "timeframe", "timestamp", name="uq_candle"
        ),
    )

    # Insert initial data for exchanges
    op.execute(
        """
        INSERT INTO exchanges (name, created_at, updated_at)
        VALUES
            ('binance', NOW(), NOW()),
            ('bybit', NOW(), NOW()),
            ('okx', NOW(), NOW())
        """
    )

    # Insert initial data for market_types
    op.execute(
        """
        INSERT INTO market_types (name, created_at, updated_at)
        VALUES
            ('spot', NOW(), NOW()),
            ('futures', NOW(), NOW())
        """
    )


def downgrade() -> None:
    op.drop_table("candles")
    op.drop_table("exchange_symbols")
    op.drop_table("symbols")
    op.drop_table("market_types")
    op.drop_table("exchanges")
