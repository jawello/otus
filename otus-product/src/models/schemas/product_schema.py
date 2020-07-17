from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.product import Product


class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

