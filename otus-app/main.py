import yaml
from aiohttp import web
from aiohttp.web import Application
from sqlalchemy import create_engine
import json

import socket
from aiohttp.web import Request, HTTPInternalServerError
from aiohttp.web_response import Response
from routes import setup_routes

import logging

log = logging.getLogger(__name__)
routes = web.RouteTableDef()


async def init_db(app):
    dsn = construct_db_url(app['config']['database'])
    pool = create_engine(dsn, pool_size=20, max_overflow=0)
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
    app = web.Application()
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


def main(config_path):
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
    args = parser.parse_args()

    main(args.config)

