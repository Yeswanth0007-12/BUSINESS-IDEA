"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-03-03 11:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_companies_id'), 'companies', ['id'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_company_id'), 'users', ['company_id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create boxes table
    op.create_table(
        'boxes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('length_cm', sa.Float(), nullable=False),
        sa.Column('width_cm', sa.Float(), nullable=False),
        sa.Column('height_cm', sa.Float(), nullable=False),
        sa.Column('cost_per_unit', sa.Float(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_boxes_company_id'), 'boxes', ['company_id'], unique=False)
    op.create_index(op.f('ix_boxes_id'), 'boxes', ['id'], unique=False)

    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('sku', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('length_cm', sa.Float(), nullable=False),
        sa.Column('width_cm', sa.Float(), nullable=False),
        sa.Column('height_cm', sa.Float(), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=False),
        sa.Column('current_box_id', sa.Integer(), nullable=True),
        sa.Column('monthly_order_volume', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['current_box_id'], ['boxes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'sku', name='uq_company_sku')
    )
    op.create_index(op.f('ix_products_company_id'), 'products', ['company_id'], unique=False)
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=False)

    # Create optimization_runs table
    op.create_table(
        'optimization_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('products_analyzed', sa.Integer(), nullable=False),
        sa.Column('total_monthly_savings', sa.Float(), nullable=False),
        sa.Column('total_annual_savings', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_optimization_runs_company_id'), 'optimization_runs', ['company_id'], unique=False)
    op.create_index(op.f('ix_optimization_runs_id'), 'optimization_runs', ['id'], unique=False)
    op.create_index(op.f('ix_optimization_runs_timestamp'), 'optimization_runs', ['timestamp'], unique=False)

    # Create optimization_results table
    op.create_table(
        'optimization_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('current_box_id', sa.Integer(), nullable=False),
        sa.Column('recommended_box_id', sa.Integer(), nullable=False),
        sa.Column('current_cost', sa.Float(), nullable=False),
        sa.Column('recommended_cost', sa.Float(), nullable=False),
        sa.Column('savings', sa.Float(), nullable=False),
        sa.Column('savings_percentage', sa.Float(), nullable=False),
        sa.Column('volumetric_weight_current', sa.Float(), nullable=False),
        sa.Column('volumetric_weight_recommended', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['current_box_id'], ['boxes.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['recommended_box_id'], ['boxes.id'], ),
        sa.ForeignKeyConstraint(['run_id'], ['optimization_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_optimization_results_id'), 'optimization_results', ['id'], unique=False)
    op.create_index(op.f('ix_optimization_results_run_id'), 'optimization_results', ['run_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_optimization_results_run_id'), table_name='optimization_results')
    op.drop_index(op.f('ix_optimization_results_id'), table_name='optimization_results')
    op.drop_table('optimization_results')
    
    op.drop_index(op.f('ix_optimization_runs_timestamp'), table_name='optimization_runs')
    op.drop_index(op.f('ix_optimization_runs_id'), table_name='optimization_runs')
    op.drop_index(op.f('ix_optimization_runs_company_id'), table_name='optimization_runs')
    op.drop_table('optimization_runs')
    
    op.drop_index(op.f('ix_products_sku'), table_name='products')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_index(op.f('ix_products_company_id'), table_name='products')
    op.drop_table('products')
    
    op.drop_index(op.f('ix_boxes_id'), table_name='boxes')
    op.drop_index(op.f('ix_boxes_company_id'), table_name='boxes')
    op.drop_table('boxes')
    
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_company_id'), table_name='users')
    op.drop_table('users')
    
    op.drop_index(op.f('ix_companies_id'), table_name='companies')
    op.drop_table('companies')
