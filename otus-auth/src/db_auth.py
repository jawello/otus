from aiohttp_security.abc import AbstractAuthorizationPolicy
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from models import Users


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, db_pool: Engine):
        self.db_pool = db_pool

    async def authorized_userid(self, identity):
        return identity

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        return True

