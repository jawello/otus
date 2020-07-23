"""Init DB

Revision ID: 75896f5e1312
Revises: 
Create Date: 2020-07-17 19:26:05.479843

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75896f5e1312'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('product',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('name', sa.String, nullable=False),
                    sa.Column('description', sa.String))


def downgrade():
    op.drop_table('product')
