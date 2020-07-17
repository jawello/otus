from typing import Callable, Awaitable

import yaml
import socket
import json

from metrics import setup_metrics

from aiohttp import web
from aiohttp.web import Application
from aiohttp.web import Request
from aiohttp.web_response import Response
from aiohttp.web_exceptions import HTTPInternalServerError
import aioredis


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

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
    setup_metrics(app, "otus-product")
    app['config'] = config
    app.add_routes(routes)

    db_pool = await init_db(app)
    db_pool = await init_db(app)
    app['db_session_manager'] = db_pool

    redis_pool = await setup_redis(app)

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

