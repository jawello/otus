from sqlalchemy import Column, String, Integer
from models import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<Users('%s','%s', '%s')>" % (str(self.id), self.login, self.password)
