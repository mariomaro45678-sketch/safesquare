"""Add listing_type_manual

Revision ID: 44048d776300
Revises: a1aa721bbc47
Create Date: 2026-02-06 14:08:54.379819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44048d776300'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('real_estate_listings', sa.Column('listing_type', sa.String(length=20), server_default='sale', nullable=True))


def downgrade() -> None:
    pass
