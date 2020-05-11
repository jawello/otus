import yaml
import socket
from aiohttp import web
from aiohttp.web import Application, Request, HTTPNoContent, HTTPNotFound, HTTPInternalServerError, HTTPBadRequest
from aiohttp.web_response import Response
import json

from models import Users
from models.schemas.users_schema import UsersSchema

from sqlalchemy.orm import sessionmaker, Session

import logging

log = logging.getLogger(__name__)
routes = web.RouteTableDef()


async def init_app(config) -> Application:
    app = web.Application()
    app['config'] = config
    app.add_routes(routes)
    log.debug(app['config'])
    return app


def load_config(config_file):
    with open(config_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


@routes.get("/health")
async def health_get(request) -> Response:
    try:
        return Response(body=json.dumps({"status": "OK"}), headers={'content-type': 'application/json'})
    except Exception as ex:
        log.warning(f"Endpoint: health, Method: get. Error:{str(ex)}")
        return HTTPInternalServerError()


@routes.get("/")
def index(request):
    try:
        return Response(body=json.dumps({"host": socket.gethostname()}), headers={'content-type': 'application/json'})
    except Exception as ex:
        log.warning(f"Endpoint: /, Method: get. Error:{str(ex)}")
        return HTTPInternalServerError()


@routes.get("/users")
async def users_get(request: Request) -> Response:
    try:
        conn = request.app['db_pool']
        session_maker = sessionmaker(bind=conn)
        session = session_maker()

        users = session.query(Users).all()

        params = request.rel_url.query.get('output')
        if params:
            output = [x.strip() for x in params.split(',')]
            users_serialized = UsersSchema(only=output, many=True).dump(users)
        else:
            users_serialized = UsersSchema(many=True).dump(users)

        return Response(body=json.dumps(users_serialized),
                        headers={'content-type': 'application/json'})

    except Exception as ex:
        log.warning(f"Endpoint: /users, Method: get. Error:{str(ex)}")
        return HTTPInternalServerError()


@routes.get("/users/{login}")
async def users_login_get(request: Request) -> Response:
    try:
        conn = request.app['db_pool']
        session_maker = sessionmaker(bind=conn)
        session: Session = session_maker()

        user = session.query(Users).filter_by(login=request.match_info['login']).first()

        if not user:
            return HTTPNotFound()

        params = request.rel_url.query.get('output')
        if params:
            output = [x.strip() for x in params.split(',')]
            user_serialized = UsersSchema(only=output).dump(user)
        else:
            user_serialized = UsersSchema().dump(user)

        return Response(body=json.dumps(user_serialized),
                        headers={'content-type': 'application/json'})
    except Exception as ex:
        log.warning(f"Endpoint: /users/login, Method: get. Error:{str(ex)}")
        return HTTPInternalServerError()


@routes.post("/users")
async def users_post(request: Request) -> Response:
    try:
        data = await request.json()

        conn = request.app['db_pool']
        session_maker = sessionmaker(bind=conn)
        session = session_maker()
        if data:
            user = UsersSchema().load(data, session=session)
            session.add(user)
            session.commit()
            return Response(headers={'Location': f"/users/{user.id}"})
        else:
            return HTTPBadRequest()
    except Exception as ex:
        log.warning(f"Endpoint: /users, Method: post. Error:{str(ex)}")
        return HTTPInternalServerError()


@routes.delete("/users/{login}")
async def users_post(request: Request) -> Response:
    try:
        conn = request.app['db_pool']
        session_maker = sessionmaker(bind=conn)
        session = session_maker()

        user = session.query(Users).filter_by(login=request.match_info['login']).first()

        if not user:
            return HTTPNotFound()

        session.delete(Users).filtre_by(login=request.match_info['login'])
        session.commit()
        return HTTPNoContent()
    except Exception as ex:
        log.warning(f"Endpoint: /users/login, Method: delete. Error:{str(ex)}")
        return HTTPInternalServerError()


def main(config_path):
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
        web.run_app(app, port=app_config.get('port', 8000))
    else:
        web.run_app(app, port=8000)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Provide path to config file")
    args = parser.parse_args()

    main(args.config)

