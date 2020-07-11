"""Init DB

Revision ID: 678c62613b3d
Revises: 
Create Date: 2020-07-05 19:06:06.686409

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '678c62613b3d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('login', sa.String, nullable=False, unique=True),
                    sa.Column('password', sa.String, nullable=False)
                    )


def downgrade():
    op.drop_table('users')
