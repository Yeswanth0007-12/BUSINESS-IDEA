"""Phase 2: Add orientation and space utilization fields to optimization_results

Revision ID: 005
Revises: 004
Create Date: 2026-03-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_phase2_orientation_fields'
down_revision = '004_enhanced_data_models'
branch_labels = None
depends_on = None


def upgrade():
    # Add Phase 2 fields to optimization_results table
    op.add_column('optimization_results', sa.Column('orientation_length', sa.Float(), nullable=True))
    op.add_column('optimization_results', sa.Column('orientation_width', sa.Float(), nullable=True))
    op.add_column('optimization_results', sa.Column('orientation_height', sa.Float(), nullable=True))
    op.add_column('optimization_results', sa.Column('space_utilization', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('optimization_results', sa.Column('unused_volume', sa.Float(), nullable=False, server_default='0.0'))


def downgrade():
    # Remove Phase 2 fields from optimization_results table
    op.drop_column('optimization_results', 'unused_volume')
    op.drop_column('optimization_results', 'space_utilization')
    op.drop_column('optimization_results', 'orientation_height')
    op.drop_column('optimization_results', 'orientation_width')
    op.drop_column('optimization_results', 'orientation_length')
