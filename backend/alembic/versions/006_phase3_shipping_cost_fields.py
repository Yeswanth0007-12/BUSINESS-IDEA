"""Phase 3: Add shipping cost fields to optimization_results

Revision ID: 006
Revises: 005
Create Date: 2026-03-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_phase3_shipping_cost_fields'
down_revision = '005_phase2_orientation_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Add Phase 3 shipping cost fields to optimization_results table
    op.add_column('optimization_results', sa.Column('shipping_cost_current', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('optimization_results', sa.Column('shipping_cost_recommended', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('optimization_results', sa.Column('total_cost_current', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('optimization_results', sa.Column('total_cost_recommended', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('optimization_results', sa.Column('billable_weight_current', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('optimization_results', sa.Column('billable_weight_recommended', sa.Float(), nullable=False, server_default='0.0'))


def downgrade():
    # Remove Phase 3 shipping cost fields from optimization_results table
    op.drop_column('optimization_results', 'billable_weight_recommended')
    op.drop_column('optimization_results', 'billable_weight_current')
    op.drop_column('optimization_results', 'total_cost_recommended')
    op.drop_column('optimization_results', 'total_cost_current')
    op.drop_column('optimization_results', 'shipping_cost_recommended')
    op.drop_column('optimization_results', 'shipping_cost_current')
