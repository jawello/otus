from sqlalchemy import Column, String, Integer
from models import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)

    def __repr__(self):
        return "<Users('%s','%s', '%s')>" % (self.name, self.login, self.password)
