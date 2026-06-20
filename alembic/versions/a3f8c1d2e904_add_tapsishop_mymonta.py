"""add tapsishop and mymonta platforms

Revision ID: a3f8c1d2e904
Revises: 10fe40270469
Create Date: 2026-06-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3f8c1d2e904'
down_revision: Union[str, Sequence[str], None] = '10fe40270469'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new enum values (must be outside transaction in older PG, but PG 12+ supports it)
    op.execute("ALTER TYPE offerplatform ADD VALUE IF NOT EXISTS 'tapsishop'")
    op.execute("ALTER TYPE offerplatform ADD VALUE IF NOT EXISTS 'mymonta'")

    # Add new URL columns to products
    op.add_column('products', sa.Column('tapsishop_url', sa.String(length=500), nullable=True))
    op.add_column('products', sa.Column('mymonta_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('products', 'mymonta_url')
    op.drop_column('products', 'tapsishop_url')
    # PostgreSQL does not support removing enum values; downgrade skips that
