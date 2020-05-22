from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.users import Users


class UsersSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        include_fk = True
        load_instance = True
