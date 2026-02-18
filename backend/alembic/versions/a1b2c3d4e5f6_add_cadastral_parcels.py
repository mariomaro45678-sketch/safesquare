"""Add cadastral_parcels table

Revision ID: a1b2c3d4e5f6
Revises: 969195dd0073
Create Date: 2026-02-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '969195dd0073'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('cadastral_parcels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('municipality_id', sa.Integer(), nullable=False),
        sa.Column('omi_zone_id', sa.Integer(), nullable=True),
        sa.Column('foglio', sa.String(length=20), nullable=False),
        sa.Column('particella', sa.String(length=30), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=4326), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['municipality_id'], ['municipalities.id']),
        sa.ForeignKeyConstraint(['omi_zone_id'], ['omi_zones.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('municipality_id', 'foglio', 'particella', name='uq_cadastral_parcel'),
    )
    op.create_index(op.f('ix_cadastral_parcels_id'), 'cadastral_parcels', ['id'], unique=False)
    # GIS spatial index on geometry (GIST) — critical for ST_Intersects performance
    op.create_index('ix_cadastral_parcels_geometry', 'cadastral_parcels', ['geometry'], postgresql_using='gist')

def downgrade():
    op.drop_index('ix_cadastral_parcels_geometry', table_name='cadastral_parcels')
    op.drop_index(op.f('ix_cadastral_parcels_id'), table_name='cadastral_parcels')
    op.drop_table('cadastral_parcels')
