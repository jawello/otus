import yaml
import socket
import json

import asyncio
from metrics import setup_metrics

from aiohttp import web
from aiohttp.web import Application
from sqlalchemy import create_engine
from aiohttp.web import Request, HTTPInternalServerError
from aiohttp.web_response import Response

from init_db.migration import alembic_set_stamp_head
from routes import setup_routes

import logging

log = logging.getLogger(__name__)

routes = web.RouteTableDef()


@asyncio.coroutine
def error_middleware(app, handler):

    @asyncio.coroutine
    def middleware_handler(request):
        try:
            response = yield from handler(request)
            return response
        except web.HTTPException as ex:
            resp = web.Response(body=str(ex), status=ex.status)
            return resp
        except Exception as ex:
            resp = web.Response(body=str(ex), status=500)
            return resp

    return middleware_handler


async def init_db(app):
    dsn = construct_db_url(app['config']['database'])
    pool = create_engine(dsn, pool_size=20, max_overflow=10)
    app['db_pool'] = pool
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
    setup_metrics(app, "otus-app")
    app['config'] = config
    app.add_routes(routes)
    setup_routes(app)
    db_pool = await init_db(app)
    app['db_pool'] = db_pool
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
def index(request: Request):
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
        setup_routes(app)
        app_config = None
    else:
        config = load_config(config_path)
        logging.basicConfig(level=logging.DEBUG)
        app = init_app(config)
        app_config = config.get('app', None)

    if app_config:
        web.run_app(app, port=app_config.get('port', 8000))
    else:
        web.run_app(app, port=8000)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Provide path to config file")
    parser.add_argument("-cm", "--config-migration", help="Provide path to config migration file")
    args = parser.parse_args()

    main(args.config, args.config_migration)

