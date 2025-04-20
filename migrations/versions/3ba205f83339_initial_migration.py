"""initial migration

Revision ID: 3ba205f83339
Revises: 
Create Date: 2024-12-02 12:00:23.054221

"""
from alembic import op
import sqlalchemy as sa

revision = '3ba205f83339'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(200)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

def downgrade():
    op.drop_table('permissions')
