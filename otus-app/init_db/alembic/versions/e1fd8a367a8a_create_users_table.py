"""create users table

Revision ID: e1fd8a367a8a
Revises: 
Create Date: 2020-05-16 22:37:20.443793

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1fd8a367a8a'
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
