import json

from aiohttp import web
from aiohttp.web import Request, HTTPBadRequest
from aiohttp.web_response import Response

from models.product import Product
from models.schemas.product_schema import ProductSchema

from sqlalchemy.orm import Session

import logging

log = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get("/products")
async def products_get(request: Request) -> Response:
    session_maker = request.app['db_session_manager']
    session: Session = session_maker()
    try:
        result = session.query(Product).all()

        products_serialized = ProductSchema(many=True).dump(result)

        return Response(body=json.dumps(products_serialized), headers={'content-type': 'application/json'})
    finally:
        session.close()


@routes.get("/products/{id}")
async def products_id_get(request: Request) -> Response:
    session_maker = request.app['db_session_manager']
    session: Session = session_maker()
    try:
        product_id = request.match_info['id']
        if not product_id:
            return HTTPBadRequest()

        product = session.query(Product).filter_by(id=product_id).first()

        products_serialized = ProductSchema().dump(product)

        return Response(body=json.dumps(products_serialized), headers={'content-type': 'application/json'})
    finally:
        session.close()


@routes.post("/products")
async def products_post(request: Request) -> Response:
    session_maker = request.app['db_session_manager']
    session: Session = session_maker()
    try:
        data = await request.json()

        if data:
            product = ProductSchema().load(data, session=session)
            session.add(product)
            session.commit()

            return Response(headers={'location': f"/products/{product.id}"})
        else:
            return HTTPBadRequest()
    finally:
        session.close()
