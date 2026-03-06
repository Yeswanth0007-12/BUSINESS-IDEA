"""create optimization tasks table

Revision ID: 008_optimization_tasks
Revises: 007_multi_product_orders
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_optimization_tasks'
down_revision = '007_multi_product_orders'
branch_labels = None
depends_on = None


def upgrade():
    """Create optimization_tasks table for tracking asynchronous task status."""
    
    # Create optimization_tasks table
    op.create_table(
        'optimization_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('result_id', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('task_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),  # Renamed from metadata
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['result_id'], ['optimization_runs.id'], ondelete='SET NULL'),
    )
    
    # Create indexes for efficient querying
    op.create_index(
        'idx_optimization_tasks_company_status',
        'optimization_tasks',
        ['company_id', 'status']
    )
    op.create_index(
        'idx_optimization_tasks_created_at',
        'optimization_tasks',
        ['created_at']
    )


def downgrade():
    """Drop optimization_tasks table and indexes."""
    
    # Drop indexes
    op.drop_index('idx_optimization_tasks_created_at', table_name='optimization_tasks')
    op.drop_index('idx_optimization_tasks_company_status', table_name='optimization_tasks')
    
    # Drop table
    op.drop_table('optimization_tasks')
