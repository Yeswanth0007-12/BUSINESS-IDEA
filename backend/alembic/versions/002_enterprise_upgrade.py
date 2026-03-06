"""Enterprise infrastructure upgrade

Revision ID: 002
Revises: 001
Create Date: 2026-03-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_enterprise_upgrade'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create subscription_plans table
    op.create_table(
        'subscription_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('price_monthly', sa.Numeric(10, 2), nullable=False),
        sa.Column('max_products', sa.Integer(), nullable=True),
        sa.Column('max_boxes', sa.Integer(), nullable=True),
        sa.Column('max_optimizations_per_month', sa.Integer(), nullable=True),
        sa.Column('max_csv_uploads_per_month', sa.Integer(), nullable=True),
        sa.Column('features', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create company_subscriptions table
    op.create_table(
        'company_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), server_default='active', nullable=False),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_roles table
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('granted_by', sa.Integer(), nullable=True),
        sa.Column('granted_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role', name='uq_user_role')
    )
    
    # Create usage_records table
    op.create_table(
        'usage_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_count', sa.Integer(), server_default='1', nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_usage_company_date', 'usage_records', ['company_id', 'created_at'])
    op.create_index('idx_usage_action_type', 'usage_records', ['action_type'])
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('old_values', postgresql.JSONB(), nullable=True),
        sa.Column('new_values', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_company_date', 'audit_logs', ['company_id', 'created_at'])
    op.create_index('idx_audit_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])
    
    # Create monthly_snapshots table
    op.create_table(
        'monthly_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.Date(), nullable=False),
        sa.Column('total_products', sa.Integer(), nullable=True),
        sa.Column('total_boxes', sa.Integer(), nullable=True),
        sa.Column('optimization_runs', sa.Integer(), nullable=True),
        sa.Column('total_cost_savings', sa.Numeric(12, 2), nullable=True),
        sa.Column('avg_space_utilization', sa.Numeric(5, 2), nullable=True),
        sa.Column('top_product_category', sa.String(100), nullable=True),
        sa.Column('most_used_box', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'month', name='uq_company_month')
    )
    op.create_index('idx_snapshots_company_month', 'monthly_snapshots', ['company_id', 'month'])
    
    # Create rate_limits table
    op.create_table(
        'rate_limits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('identifier', sa.String(100), nullable=False),
        sa.Column('endpoint', sa.String(200), nullable=False),
        sa.Column('request_count', sa.Integer(), server_default='1', nullable=False),
        sa.Column('window_start', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier', 'endpoint', 'window_start', name='uq_rate_limit')
    )
    op.create_index('idx_rate_limits_lookup', 'rate_limits', ['identifier', 'endpoint', 'window_start'])
    
    # Add indexes to existing tables
    op.create_index('idx_products_company', 'products', ['company_id'])
    op.create_index('idx_products_category', 'products', ['category'])
    op.create_index('idx_products_sku', 'products', ['sku'])
    
    op.create_index('idx_boxes_company', 'boxes', ['company_id'])
    op.create_index('idx_boxes_cost', 'boxes', ['cost_per_unit'])
    
    op.create_index('idx_optimization_runs_company', 'optimization_runs', ['company_id'])
    op.create_index('idx_optimization_runs_date', 'optimization_runs', ['timestamp'])
    
    op.create_index('idx_optimization_results_run', 'optimization_results', ['run_id'])
    
    # Add new columns to existing tables
    op.add_column('products', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('boxes', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('login_count', sa.Integer(), server_default='0', nullable=False))
    
    op.add_column('companies', sa.Column('settings', postgresql.JSONB(), server_default='{}', nullable=False))
    
    # Insert default subscription plans
    op.execute("""
        INSERT INTO subscription_plans (name, price_monthly, max_products, max_boxes, max_optimizations_per_month, max_csv_uploads_per_month, features)
        VALUES 
        ('FREE', 0.00, 50, 10, 10, 5, '{"analytics": "basic", "support": "email"}'),
        ('PRO', 49.00, 500, 50, 100, 50, '{"analytics": "advanced", "support": "priority", "export": true}'),
        ('ENTERPRISE', 199.00, NULL, NULL, NULL, NULL, '{"analytics": "custom", "support": "dedicated", "export": true, "api_access": true, "audit_logs": true, "white_label": true}')
    """)
    
    # Assign all existing companies to free plan
    op.execute("""
        INSERT INTO company_subscriptions (company_id, plan_id, status)
        SELECT id, (SELECT id FROM subscription_plans WHERE name = 'FREE'), 'active'
        FROM companies
    """)
    
    # Assign admin role to all existing users (first user of each company)
    op.execute("""
        INSERT INTO user_roles (user_id, role)
        SELECT DISTINCT ON (company_id) id, 'admin'
        FROM users
        ORDER BY company_id, id
    """)


def downgrade() -> None:
    # Remove indexes from existing tables
    op.drop_index('idx_optimization_results_run', 'optimization_results')
    op.drop_index('idx_optimization_runs_date', 'optimization_runs')
    op.drop_index('idx_optimization_runs_company', 'optimization_runs')
    op.drop_index('idx_boxes_cost', 'boxes')
    op.drop_index('idx_boxes_company', 'boxes')
    op.drop_index('idx_products_sku', 'products')
    op.drop_index('idx_products_category', 'products')
    op.drop_index('idx_products_company', 'products')
    
    # Remove new columns from existing tables
    op.drop_column('companies', 'settings')
    op.drop_column('users', 'login_count')
    op.drop_column('users', 'last_login_at')
    op.drop_column('boxes', 'deleted_at')
    op.drop_column('products', 'deleted_at')
    
    # Drop new tables
    op.drop_index('idx_rate_limits_lookup', 'rate_limits')
    op.drop_table('rate_limits')
    
    op.drop_index('idx_snapshots_company_month', 'monthly_snapshots')
    op.drop_table('monthly_snapshots')
    
    op.drop_index('idx_audit_resource', 'audit_logs')
    op.drop_index('idx_audit_user', 'audit_logs')
    op.drop_index('idx_audit_company_date', 'audit_logs')
    op.drop_table('audit_logs')
    
    op.drop_index('idx_usage_action_type', 'usage_records')
    op.drop_index('idx_usage_company_date', 'usage_records')
    op.drop_table('usage_records')
    
    op.drop_table('user_roles')
    op.drop_table('company_subscriptions')
    op.drop_table('subscription_plans')
