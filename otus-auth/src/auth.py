from typing import Callable, Awaitable

import yaml
import socket
import json

from metrics import setup_metrics

import aiohttp
from aiohttp import web, ClientError, InvalidURL, ClientResponseError
from aiohttp.web import Application
from aiohttp.web import Request
from aiohttp.web_response import Response
from aiohttp.web_exceptions import HTTPConflict, HTTPCreated, HTTPBadRequest, HTTPAccepted, HTTPUnauthorized, \
    HTTPNoContent, HTTPInternalServerError, HTTPNotAcceptable, HTTPNotFound
from aiohttp_security import remember, authorized_userid, forget, check_permission
from aiohttp_session.redis_storage import RedisStorage
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from aiohttp_session import setup as setup_session
import aioredis

from db_auth import DBAuthorizationPolicy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models import Users
from models.schemas.users_schema import UsersSchema

from init_db.migration import alembic_set_stamp_head

import logging

log = logging.getLogger(__name__)

routes = web.RouteTableDef()


@web.middleware
async def error_middleware(request: web.Request, handler: Callable[[web.Request], Awaitable[web.StreamResponse]]) \
        -> web.StreamResponse:
    try:
        return await handler(request)
    except web.HTTPException as ex:
        resp = web.Response(body=str(ex), status=ex.status)
        return resp
    except Exception as ex:
        log.warning(f"Endpoint: {request.path}, Method: {request.method}. Error:{str(ex)}")
        resp = HTTPInternalServerError(body=str(ex))
        return resp


async def setup_redis(app):
    pool = await aioredis.create_redis_pool((
        app['config']['redis']['REDIS_HOST'],
        app['config']['redis']['REDIS_PORT']
    ))

    async def close_redis(app):
        pool.close()
        await pool.wait_closed()

    app.on_cleanup.append(close_redis)
    app['redis_pool'] = pool
    return pool


async def init_db(app):
    dsn = construct_db_url(app['config']['database'])
    pool = create_engine(dsn, pool_size=20, max_overflow=10)
    app['db_session_manager'] = sessionmaker(bind=pool)
    return pool


def construct_db_url(config):
    dsn = "postgresql://{user}:{password}@{host}:{port}/{database}"
    return dsn.format(
        user=config['DB_USER'],
        password=config['DB_PASS'],
        database=config['DB_NAME'],
        host=config['DB_HOST'],
        port=config['DB_PORT'],
    )


async def init_app(config) -> Application:
    app = web.Application(middlewares=[error_middleware])
    setup_metrics(app, "otus-auth")
    app['config'] = config
    app.add_routes(routes)

    db_pool = await init_db(app)

    redis_pool = await setup_redis(app)
    setup_session(app, RedisStorage(redis_pool))
    setup_security(
        app,
        SessionIdentityPolicy(),
        DBAuthorizationPolicy(db_pool)
    )

    log.debug(app['config'])
    return app


def load_config(config_file):
    import os
    print(os.getcwd())
    with open(config_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


@routes.get("/health")
async def health_get(request: Request) -> Response:
    try:
        return Response(body=json.dumps({"status": "OK"}), headers={'content-type': 'application/json'})
    except Exception as ex:
        log.warning(f"Endpoint: health, Method: get. Error:{str(ex)}")
        return HTTPInternalServerError()


@routes.get("/")
async def index(request: Request):
    try:
        return Response(body=json.dumps({"host": socket.gethostname()}), headers={'content-type': 'application/json'})
    except Exception as ex:
        log.warning(f"Endpoint: /, Method: get. Error:{str(ex)}")
        return HTTPInternalServerError()


@routes.post("/registration")
async def registration(request: Request):

    if 'X-UserId' in request.headers:
        return HTTPNotAcceptable()

    session_maker = request.app['db_session_manager']
    session: Session = session_maker()
    try:
        data = await request.json()

        if data:
            user_db = session.query(Users).filter_by(login=data['login']).first()
            if user_db:
                return HTTPConflict()

            data_without_password = dict(data)
            data_without_password.pop('password')

            data_for_auth = {'login': data['login'], 'password': data['password']}
            if 'account_manager' in request.app['config']['app']:
                url = request.app['config']['app']['account_manager']['url']
                async with aiohttp.ClientSession(raise_for_status=True) as http_client_session:
                    async with http_client_session.post(url, json=data_without_password) as \
                            resp:
                        account_manager_resp = await resp.json()
                data_for_auth['id'] = account_manager_resp['id']
                user_serializer = UsersSchema().load(data_for_auth, session=session)
            else:
                user_serializer = UsersSchema().load(data_for_auth, session=session)

            session.add(user_serializer)
            session.commit()
            return HTTPCreated(headers={'Location': f"/users/{user_serializer.login}"})
        else:
            return HTTPBadRequest()
    except InvalidURL as ex:
        raise Exception(f"""Invalid url account_manager:{str(ex)}""")
    except ClientResponseError:
        return HTTPConflict()
    except ClientError as ex:
        raise Exception(f"""Can't connect to account_manager:{str(ex)}""")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@routes.post("/session")
async def session_post(request: Request):
    session_maker = request.app['db_session_manager']
    session: Session = session_maker()
    try:
        data = await request.json()

        if data:
            user = session.query(Users).filter_by(login=data['login']).first()
            if not user:
                return HTTPNotFound()

            user_id = await authorized_userid(request)
            if UsersSchema.check_password_hash(data['password'], user.password):
                response = HTTPAccepted()
                await remember(request, response, str(user.id))
                return response
            else:
                response = HTTPUnauthorized()
                if user_id:
                    await forget(request, response)
                return response
        else:
            return HTTPBadRequest()
    except Exception:
        raise
    finally:
        session.close()


@routes.delete("/session")
async def session_post(request: Request):
    try:
        user_id = await authorized_userid(request)
        if not user_id:
            return HTTPUnauthorized()
        await forget(request, HTTPNoContent())
        return HTTPNoContent()
    except Exception:
        raise


@routes.route("*", "/auth")
async def auth(request: Request):
    user_id = await authorized_userid(request)
    if not user_id:
        return HTTPUnauthorized()

    return Response(headers={'X-UserId': user_id})


@routes.get("/signin")
async def signin_get(request: Request):
    user_id = await authorized_userid(request)
    if not user_id:
        return HTTPUnauthorized()
    return Response(body=json.dumps({"message": "Please go to /session and provide Login/Password"}))


def main(config_path, config_migration_path):
    if config_migration_path:
        alembic_set_stamp_head(config_migration_path)
    if not config_path:
        app = web.Application()
        app.add_routes(routes)
        app_config = None
    else:
        config = load_config(config_path)
        logging.basicConfig(level=logging.DEBUG)
        app = init_app(config)
        app_config = config.get('app', None)

    if app_config:
        web.run_app(app, port=app_config.get('port', 9000))
    else:
        web.run_app(app, port=9000)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Provide path to config file")
    parser.add_argument("-cm", "--config-migration", help="Provide path to config migration file")
    args = parser.parse_args()

    main(args.config, args.config_migration)

