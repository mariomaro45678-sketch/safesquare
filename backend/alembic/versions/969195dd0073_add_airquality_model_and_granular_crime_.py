"""Add AirQuality model and granular crime fields

Revision ID: 969195dd0073
Revises: 8cc43f8731ad
Create Date: 2026-01-30 16:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '969195dd0073'
down_revision = '8cc43f8731ad'
branch_labels = None
depends_on = None

def upgrade():
    # Create air_quality table
    op.create_table('air_quality',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('municipality_id', sa.Integer(), nullable=False),
        sa.Column('pm25_avg', sa.Float(), nullable=True),
        sa.Column('pm10_avg', sa.Float(), nullable=True),
        sa.Column('no2_avg', sa.Float(), nullable=True),
        sa.Column('o3_avg', sa.Float(), nullable=True),
        sa.Column('aqi_index', sa.Float(), nullable=True),
        sa.Column('health_risk_level', sa.String(length=20), nullable=True),
        sa.Column('station_count', sa.Integer(), nullable=True),
        sa.Column('data_source', sa.String(length=100), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['municipality_id'], ['municipalities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_air_quality_id'), 'air_quality', ['id'], unique=False)

    # Add columns to crime_statistics
    op.add_column('crime_statistics', sa.Column('burglary_rate', sa.Float(), nullable=True))
    op.add_column('crime_statistics', sa.Column('vandalism_rate', sa.Float(), nullable=True))
    op.add_column('crime_statistics', sa.Column('theft_rate', sa.Float(), nullable=True))
    op.add_column('crime_statistics', sa.Column('crime_metadata', sa.JSON(), nullable=True))

def downgrade():
    op.drop_column('crime_statistics', 'crime_metadata')
    op.drop_column('crime_statistics', 'theft_rate')
    op.drop_column('crime_statistics', 'vandalism_rate')
    op.drop_column('crime_statistics', 'burglary_rate')
    op.drop_index(op.f('ix_air_quality_id'), table_name='air_quality')
    op.drop_table('air_quality')
