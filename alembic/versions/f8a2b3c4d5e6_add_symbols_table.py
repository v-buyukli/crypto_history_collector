"""Add symbols table, normalize candles, add timestamps to all models

Revision ID: f8a2b3c4d5e6
Revises: ce2c3ffc8450
Create Date: 2026-01-18

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f8a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "ce2c3ffc8450"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add symbols table, migrate candles.symbol to symbol_id, add timestamps."""
    # 1. Create symbols table with timestamps
    op.create_table(
        "symbols",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # 2. Add timestamps to exchanges table
    op.add_column(
        "exchanges",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.add_column(
        "exchanges",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # 3. Add timestamps to market_types table
    op.add_column(
        "market_types",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.add_column(
        "market_types",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # 4. Add updated_at to candles table
    op.add_column(
        "candles",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # 5. Add symbol_id column to candles (nullable for now)
    op.add_column("candles", sa.Column("symbol_id", sa.Integer(), nullable=True))

    # 6. Migrate data: create symbols from unique candles.symbol values
    op.execute(
        """
        INSERT INTO symbols (name)
        SELECT DISTINCT symbol FROM candles
        ON CONFLICT (name) DO NOTHING;
    """
    )

    # 7. Populate symbol_id in candles based on symbol name
    op.execute(
        """
        UPDATE candles
        SET symbol_id = symbols.id
        FROM symbols
        WHERE candles.symbol = symbols.name;
    """
    )

    # 8. Make symbol_id NOT NULL
    op.alter_column("candles", "symbol_id", nullable=False)

    # 9. Add foreign key constraint
    op.create_foreign_key(
        "fk_candles_symbol_id",
        "candles",
        "symbols",
        ["symbol_id"],
        ["id"],
    )

    # 10. Drop old unique constraint (if exists)
    op.execute(
        """
        ALTER TABLE candles DROP CONSTRAINT IF EXISTS uq_candle;
    """
    )

    # 11. Drop old symbol column
    op.drop_column("candles", "symbol")

    # 12. Create new unique constraint with symbol_id
    op.create_unique_constraint(
        "uq_candle",
        "candles",
        ["exchange_id", "market_type_id", "symbol_id", "timeframe", "timestamp"],
    )


def downgrade() -> None:
    """Revert symbols table, restore candles.symbol column, remove timestamps."""
    # 1. Drop new unique constraint (if exists)
    op.execute(
        """
        ALTER TABLE candles DROP CONSTRAINT IF EXISTS uq_candle;
    """
    )

    # 2. Add back symbol column
    op.add_column("candles", sa.Column("symbol", sa.String(length=100), nullable=True))

    # 3. Populate symbol from symbols table
    op.execute(
        """
        UPDATE candles
        SET symbol = symbols.name
        FROM symbols
        WHERE candles.symbol_id = symbols.id;
    """
    )

    # 4. Make symbol NOT NULL
    op.alter_column("candles", "symbol", nullable=False)

    # 5. Drop foreign key constraint (if exists)
    op.execute(
        """
        ALTER TABLE candles DROP CONSTRAINT IF EXISTS fk_candles_symbol_id;
    """
    )

    # 6. Drop symbol_id column
    op.drop_column("candles", "symbol_id")

    # 7. Restore original unique constraint
    op.create_unique_constraint(
        "uq_candle",
        "candles",
        ["exchange_id", "market_type_id", "symbol", "timeframe", "timestamp"],
    )

    # 8. Drop updated_at from candles
    op.drop_column("candles", "updated_at")

    # 9. Drop timestamps from market_types
    op.drop_column("market_types", "updated_at")
    op.drop_column("market_types", "created_at")

    # 10. Drop timestamps from exchanges
    op.drop_column("exchanges", "updated_at")
    op.drop_column("exchanges", "created_at")

    # 11. Drop symbols table
    op.drop_table("symbols")
