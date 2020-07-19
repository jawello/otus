from typing import Callable, Awaitable

import socket
import json

from metrics import setup_metrics

from aiohttp import web
from aiohttp.web import Application
from aiohttp.web import Request
from aiohttp.web_response import Response
from aiohttp.web_exceptions import HTTPInternalServerError
from aiohttp_cache import (
    setup_cache,
    RedisConfig
)

from db import init_db
from config import load_config

from init_db.migration import alembic_set_stamp_head

from routes import setup_routes

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


def setup_redis(app: web.Application, config_redis: dict):
    setup_cache(
        app,
        cache_type="redis",
        backend_config=RedisConfig(host=config_redis.get('host', 'localhost'),
                                   port=config_redis.get('port', 6379)
                                   )
    )


def init_app(config) -> Application:
    app = web.Application(middlewares=[error_middleware])
    setup_metrics(app, "otus-product")
    app['config'] = config
    app.add_routes(routes)
    setup_routes(app)

    init_db(app)

    if 'redis' in app['config']:
        setup_redis(app, config['redis'])

    log.debug(app['config'])
    return app


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

