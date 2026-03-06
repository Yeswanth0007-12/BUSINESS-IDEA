"""bulk uploads

Revision ID: 009_bulk_uploads
Revises: 008_optimization_tasks
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_bulk_uploads'
down_revision = '008_optimization_tasks'
branch_labels = None
depends_on = None


def upgrade():
    # Create bulk_uploads table
    op.create_table(
        'bulk_uploads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('total_orders', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('processed_orders', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('failed_orders', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='uploading'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bulk_uploads_company_id'), 'bulk_uploads', ['company_id'], unique=False)
    op.create_index(op.f('ix_bulk_uploads_status'), 'bulk_uploads', ['status'], unique=False)
    
    # Create bulk_upload_orders table
    op.create_table(
        'bulk_upload_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('upload_id', sa.Integer(), nullable=False),
        sa.Column('row_number', sa.Integer(), nullable=False),
        sa.Column('order_data', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('task_id', sa.String(length=255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['upload_id'], ['bulk_uploads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bulk_upload_orders_upload_id'), 'bulk_upload_orders', ['upload_id'], unique=False)
    op.create_index(op.f('ix_bulk_upload_orders_status'), 'bulk_upload_orders', ['status'], unique=False)


def downgrade():
    # Drop bulk_upload_orders table
    op.drop_index(op.f('ix_bulk_upload_orders_status'), table_name='bulk_upload_orders')
    op.drop_index(op.f('ix_bulk_upload_orders_upload_id'), table_name='bulk_upload_orders')
    op.drop_table('bulk_upload_orders')
    
    # Drop bulk_uploads table
    op.drop_index(op.f('ix_bulk_uploads_status'), table_name='bulk_uploads')
    op.drop_index(op.f('ix_bulk_uploads_company_id'), table_name='bulk_uploads')
    op.drop_table('bulk_uploads')
