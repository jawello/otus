"""create users table

Revision ID: 90896555d38a
Revises: 
Create Date: 2020-05-11 22:09:43.368399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90896555d38a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('login', sa.String, nullable=False, unique=True),
                    sa.Column('first_name', sa.String, nullable=False),
                    sa.Column('last_name', sa.String, nullable=False),
                    sa.Column('email', sa.String, nullable=False),
                    sa.Column('phone', sa.String, nullable=False)
                    )


def downgrade():
    op.drop_table('users')
