"""fix optimization nullable current_box_id

Revision ID: 003
Revises: 002
Create Date: 2026-03-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_fix_optimization_nullable'
down_revision = '002_enterprise_upgrade'
branch_labels = None
depends_on = None


def upgrade():
    # Make current_box_id nullable in optimization_results
    op.alter_column('optimization_results', 'current_box_id',
                    existing_type=sa.Integer(),
                    nullable=True)


def downgrade():
    # Revert to non-nullable
    op.alter_column('optimization_results', 'current_box_id',
                    existing_type=sa.Integer(),
                    nullable=False)
