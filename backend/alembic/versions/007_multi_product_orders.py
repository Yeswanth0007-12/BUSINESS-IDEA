"""Phase 4: Multi-product order tables

Revision ID: 007
Revises: 006
Create Date: 2026-03-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_multi_product_orders'
down_revision = '006_phase3_shipping_cost_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(100), nullable=False),
        sa.Column('customer_name', sa.String(200), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'order_number', name='uq_company_order_number')
    )
    op.create_index('ix_orders_id', 'orders', ['id'])
    op.create_index('ix_orders_company_id', 'orders', ['company_id'])
    op.create_index('ix_orders_order_number', 'orders', ['order_number'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    
    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_items_id', 'order_items', ['id'])
    op.create_index('ix_order_items_order_id', 'order_items', ['order_id'])
    
    # Create order_packing_results table
    op.create_table(
        'order_packing_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('box_id', sa.Integer(), nullable=False),
        sa.Column('box_number', sa.Integer(), nullable=False),
        sa.Column('products_packed', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('total_weight', sa.Float(), nullable=False),
        sa.Column('space_utilization', sa.Float(), nullable=False),
        sa.Column('shipping_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['box_id'], ['boxes.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_packing_results_id', 'order_packing_results', ['id'])
    op.create_index('ix_order_packing_results_order_id', 'order_packing_results', ['order_id'])


def downgrade():
    # Drop tables in reverse order
    op.drop_index('ix_order_packing_results_order_id', 'order_packing_results')
    op.drop_index('ix_order_packing_results_id', 'order_packing_results')
    op.drop_table('order_packing_results')
    
    op.drop_index('ix_order_items_order_id', 'order_items')
    op.drop_index('ix_order_items_id', 'order_items')
    op.drop_table('order_items')
    
    op.drop_index('ix_orders_status', 'orders')
    op.drop_index('ix_orders_order_number', 'orders')
    op.drop_index('ix_orders_company_id', 'orders')
    op.drop_index('ix_orders_id', 'orders')
    op.drop_table('orders')
