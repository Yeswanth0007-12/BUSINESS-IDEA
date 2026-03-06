"""analytics tables

Revision ID: 010_analytics_tables
Revises: 009_bulk_uploads
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010_analytics_tables'
down_revision = '009_bulk_uploads'
branch_labels = None
depends_on = None


def upgrade():
    """Create analytics tables for advanced metrics tracking."""
    
    # Create analytics_snapshots table
    op.create_table(
        'analytics_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('total_products', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_boxes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_optimizations', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_space_utilization', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_monthly_savings', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_annual_savings', sa.Float(), nullable=False, server_default='0.0'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'snapshot_date', name='uq_company_snapshot_date')
    )
    op.create_index('idx_analytics_company_date', 'analytics_snapshots', ['company_id', 'snapshot_date'])
    op.create_index(op.f('ix_analytics_snapshots_id'), 'analytics_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_analytics_snapshots_snapshot_date'), 'analytics_snapshots', ['snapshot_date'], unique=False)
    
    # Create box_usage_metrics table
    op.create_table(
        'box_usage_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('box_id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avg_utilization', sa.Float(), nullable=False, server_default='0.0'),
        sa.ForeignKeyConstraint(['box_id'], ['boxes.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_box_usage_company', 'box_usage_metrics', ['company_id'])
    op.create_index('idx_box_usage_period', 'box_usage_metrics', ['period_start', 'period_end'])
    op.create_index(op.f('ix_box_usage_metrics_id'), 'box_usage_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_box_usage_metrics_period_end'), 'box_usage_metrics', ['period_end'], unique=False)
    op.create_index(op.f('ix_box_usage_metrics_period_start'), 'box_usage_metrics', ['period_start'], unique=False)
    
    # Create shipping_cost_metrics table
    op.create_table(
        'shipping_cost_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('total_shipments', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_shipping_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avg_billable_weight', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('volumetric_weight_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_shipping_cost_company', 'shipping_cost_metrics', ['company_id'])
    op.create_index('idx_shipping_cost_period', 'shipping_cost_metrics', ['period_start', 'period_end'])
    op.create_index(op.f('ix_shipping_cost_metrics_id'), 'shipping_cost_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_shipping_cost_metrics_period_end'), 'shipping_cost_metrics', ['period_end'], unique=False)
    op.create_index(op.f('ix_shipping_cost_metrics_period_start'), 'shipping_cost_metrics', ['period_start'], unique=False)


def downgrade():
    """Drop analytics tables."""
    
    # Drop shipping_cost_metrics table
    op.drop_index(op.f('ix_shipping_cost_metrics_period_start'), table_name='shipping_cost_metrics')
    op.drop_index(op.f('ix_shipping_cost_metrics_period_end'), table_name='shipping_cost_metrics')
    op.drop_index(op.f('ix_shipping_cost_metrics_id'), table_name='shipping_cost_metrics')
    op.drop_index('idx_shipping_cost_period', table_name='shipping_cost_metrics')
    op.drop_index('idx_shipping_cost_company', table_name='shipping_cost_metrics')
    op.drop_table('shipping_cost_metrics')
    
    # Drop box_usage_metrics table
    op.drop_index(op.f('ix_box_usage_metrics_period_start'), table_name='box_usage_metrics')
    op.drop_index(op.f('ix_box_usage_metrics_period_end'), table_name='box_usage_metrics')
    op.drop_index(op.f('ix_box_usage_metrics_id'), table_name='box_usage_metrics')
    op.drop_index('idx_box_usage_period', table_name='box_usage_metrics')
    op.drop_index('idx_box_usage_company', table_name='box_usage_metrics')
    op.drop_table('box_usage_metrics')
    
    # Drop analytics_snapshots table
    op.drop_index(op.f('ix_analytics_snapshots_snapshot_date'), table_name='analytics_snapshots')
    op.drop_index(op.f('ix_analytics_snapshots_id'), table_name='analytics_snapshots')
    op.drop_index('idx_analytics_company_date', table_name='analytics_snapshots')
    op.drop_table('analytics_snapshots')
