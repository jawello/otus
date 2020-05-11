from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from models import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    login = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<Users('%s','%s', '%s')>" % (self.name, self.login, self.password)
