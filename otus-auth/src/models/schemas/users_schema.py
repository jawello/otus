from marshmallow_sqlalchemy import SQLAlchemySchema
from models.users import Users
from marshmallow import fields
import bcrypt


class PasswordCrypt(fields.Field):
    @staticmethod
    def generate_password_hash(password):
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        return hashed

    def _deserialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        return PasswordCrypt.generate_password_hash(value)

    def _serialize(self, value, attr, data, **kwargs):
        return value


class UsersSchema(SQLAlchemySchema):
    class Meta:
        model = Users
        load_instance = True

    id = fields.Integer()
    login = fields.String()
    password = PasswordCrypt()

    @staticmethod
    def check_password_hash(plain_password, password_hash):
        return bcrypt.checkpw(plain_password, password_hash)
