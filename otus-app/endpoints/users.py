from aiohttp.web import Request, HTTPInternalServerError, HTTPNotFound, HTTPConflict, HTTPBadRequest, HTTPNoContent
from aiohttp.web_response import Response
import json
from aiohttp import web

from models import Users
from models.schemas.users_schema import UsersSchema

from sqlalchemy.orm import sessionmaker, Session

import logging
log = logging.getLogger(__name__)

routes = web.RouteTableDef()


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
            user = session.query(Users).filter_by(login=data['login']).first()
            if user:
                return HTTPConflict()

            user = UsersSchema().load(data, session=session)

            session.add(user)
            session.commit()
            return Response(headers={'Location': f"/users/{user.login}"})
        else:
            return HTTPBadRequest()
    except Exception as ex:
        log.warning(f"Endpoint: /users, Method: post. Error:{str(ex)}")
        return HTTPInternalServerError()


@routes.put("/users/{login}")
async def users_put(request: Request) -> Response:
    try:
        data = await request.json()

        conn = request.app['db_pool']
        session_maker = sessionmaker(bind=conn)
        session = session_maker()

        if data:
            user = session.query(Users).filter_by(login=request.match_info['login']).first()
            if not user:
                return HTTPNotFound()

            user_put = UsersSchema().load(data, session=session, partial=True)

            user.first_name = user_put.first_name
            user.last_name = user_put.last_name
            user.email = user_put.email
            user.phone = user_put.phone

            session.commit()
            return Response(headers={'Location': f"/users/{user.login}"})
        else:
            return HTTPBadRequest()
    except Exception as ex:
        log.warning(f"Endpoint: /users/login, Method: put. Error:{str(ex)}")
        return HTTPInternalServerError()


@routes.delete("/users/{login}")
async def users_delete(request: Request) -> Response:
    try:
        conn = request.app['db_pool']
        session_maker = sessionmaker(bind=conn)
        session = session_maker()

        user = session.query(Users).filter_by(login=request.match_info['login']).first()

        if not user:
            return HTTPNotFound()

        session.delete(user)
        session.commit()
        return HTTPNoContent()
    except Exception as ex:
        log.warning(f"Endpoint: /users/login, Method: delete. Error:{str(ex)}")
        return HTTPInternalServerError()
