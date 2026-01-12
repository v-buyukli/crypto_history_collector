"""Add initial exchanges and market types

Revision ID: ce2c3ffc8450
Revises: a3daaced5340
Create Date: 2026-01-12 10:57:37.959687

"""

from typing import Sequence, Union

from sqlalchemy import String, column, table

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ce2c3ffc8450"
down_revision: Union[str, Sequence[str], None] = "a3daaced5340"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add initial data."""
    exchanges_table = table("exchanges", column("name", String))
    market_types_table = table("market_types", column("name", String))

    # Insert exchanges
    op.bulk_insert(
        exchanges_table,
        [
            {"name": "binance"},
            {"name": "bybit"},
            {"name": "okx"},
        ],
    )

    # Insert market types
    op.bulk_insert(
        market_types_table,
        [
            {"name": "spot"},
            {"name": "futures"},
        ],
    )


def downgrade() -> None:
    """Remove initial data."""
    # Delete in reverse order
    op.execute("DELETE FROM market_types WHERE name IN ('spot', 'futures')")
    op.execute("DELETE FROM exchanges WHERE name IN ('binance', 'bybit', 'okx')")
