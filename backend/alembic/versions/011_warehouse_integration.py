"""warehouse integration

Revision ID: 011_warehouse_integration
Revises: 010_analytics_tables
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '011_warehouse_integration'
down_revision = '010_analytics_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )
    op.create_index(op.f('ix_api_keys_id'), 'api_keys', ['id'], unique=False)
    op.create_index(op.f('ix_api_keys_company_id'), 'api_keys', ['company_id'], unique=False)
    
    # Create webhooks table
    op.create_table(
        'webhooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('events', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('secret', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhooks_id'), 'webhooks', ['id'], unique=False)
    op.create_index(op.f('ix_webhooks_company_id'), 'webhooks', ['company_id'], unique=False)
    
    # Create webhook_deliveries table
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('webhook_id', sa.Integer(), nullable=False),
        sa.Column('event', sa.String(length=100), nullable=False),
        sa.Column('payload', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhooks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webhook_deliveries_id'), 'webhook_deliveries', ['id'], unique=False)
    op.create_index(op.f('ix_webhook_deliveries_webhook_id'), 'webhook_deliveries', ['webhook_id'], unique=False)
    op.create_index(op.f('ix_webhook_deliveries_created_at'), 'webhook_deliveries', ['created_at'], unique=False)


def downgrade():
    # Drop webhook_deliveries table
    op.drop_index(op.f('ix_webhook_deliveries_created_at'), table_name='webhook_deliveries')
    op.drop_index(op.f('ix_webhook_deliveries_webhook_id'), table_name='webhook_deliveries')
    op.drop_index(op.f('ix_webhook_deliveries_id'), table_name='webhook_deliveries')
    op.drop_table('webhook_deliveries')
    
    # Drop webhooks table
    op.drop_index(op.f('ix_webhooks_company_id'), table_name='webhooks')
    op.drop_index(op.f('ix_webhooks_id'), table_name='webhooks')
    op.drop_table('webhooks')
    
    # Drop api_keys table
    op.drop_index(op.f('ix_api_keys_company_id'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_id'), table_name='api_keys')
    op.drop_table('api_keys')
