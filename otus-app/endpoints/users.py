from aiohttp.web import Request, HTTPNotFound, HTTPConflict, HTTPBadRequest, HTTPNoContent, \
    HTTPCreated
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
    session_maker = request.app['db_session_manager']
    session: Session = session_maker()
    try:
        users = session.query(Users).all()
        params = request.rel_url.query.get('output')
        if params:
            output = [x.strip() for x in params.split(',')]
            users_serialized = UsersSchema(only=output, many=True).dump(users)
        else:
            users_serialized = UsersSchema(many=True).dump(users)
        return Response(body=json.dumps(users_serialized),
                        headers={'content-type': 'application/json'})

    finally:
        session.close()


@routes.get("/users/{login}")
async def users_login_get(request: Request) -> Response:
    session_maker = request.app['db_session_manager']
    session: Session = session_maker()
    try:
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

    finally:
        session.close()


@routes.post("/users")
async def users_post(request: Request) -> Response:
    session_maker = request.app['db_session_manager']
    session: Session = session_maker()
    try:
        data = await request.json()

        if data:
            user = session.query(Users).filter_by(login=data['login']).first()
            if user:
                return HTTPConflict()

            user = UsersSchema().load(data, session=session)

            session.add(user)
            session.commit()
            return HTTPCreated(headers={'Location': f"/users/{user.login}"}, body=json.dumps({'id': user.id}))
        else:
            return HTTPBadRequest()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@routes.put("/users/{login}")
async def users_put(request: Request) -> Response:
    session_maker = request.app['db_session_manager']
    session: Session = session_maker()
    try:
        data = await request.json()

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
            return HTTPNoContent(headers={'Location': f"/users/{user.login}"})
        else:
            session.close()
            return HTTPBadRequest()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@routes.delete("/users/{login}")
async def users_delete(request: Request) -> Response:
    session_maker = request.app['db_session_manager']
    session: Session = session_maker()
    try:

        user = session.query(Users).filter_by(login=request.match_info['login']).first()

        if not user:
            session.close()
            return HTTPNotFound()

        session.delete(user)
        session.commit()
        return HTTPNoContent()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
