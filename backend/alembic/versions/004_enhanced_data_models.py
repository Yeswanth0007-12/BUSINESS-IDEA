"""Enhanced data models for production logistics

Revision ID: 004
Revises: 003
Create Date: 2026-03-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_enhanced_data_models'
down_revision = '003_fix_optimization_nullable'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to products table
    op.add_column('products', sa.Column('fragile', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('products', sa.Column('stackable', sa.Boolean(), server_default='true', nullable=False))
    
    # Add new columns to boxes table
    op.add_column('boxes', sa.Column('max_weight_kg', sa.Float(), server_default='30.0', nullable=False))
    op.add_column('boxes', sa.Column('material_type', sa.String(50), server_default='cardboard', nullable=False))


def downgrade() -> None:
    # Remove columns from boxes table
    op.drop_column('boxes', 'material_type')
    op.drop_column('boxes', 'max_weight_kg')
    
    # Remove columns from products table
    op.drop_column('products', 'stackable')
    op.drop_column('products', 'fragile')
