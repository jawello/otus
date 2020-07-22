import sqlalchemy as sa

from models import Base


class Product(Base):
    __tablename__ = 'product'
    id = sa.Column('id', sa.Integer, primary_key=True)
    name = sa.Column('name', sa.String, nullable=False, unique=True)
    description = sa.Column('description', sa.String)

    def __repr__(self):
        return "<Product('%s','%s', '%s')>" % (self.id, self.name, self.description)
