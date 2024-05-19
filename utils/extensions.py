from flask import g
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy as SQLAlchemyBase
from sqlalchemy.orm import Query, scoped_session, sessionmaker

from utils.celery_utils import make_celery


class UserScopedQuery(Query):
    def get(self, ident):
        current_user_id = g.get("user_id", None)
        return (
            super().filter_by(user_id=current_user_id).get(ident)
            if current_user_id
            else None
        )

    def all(self):
        current_user_id = g.get("user_id", None)
        return (
            super().filter_by(user_id=current_user_id).all() if current_user_id else []
        )

    def first(self):
        current_user_id = g.get("user_id", None)
        return (
            super().filter_by(user_id=current_user_id).first()
            if current_user_id
            else None
        )


class SQLAlchemy(SQLAlchemyBase):
    def create_scoped_session(self, options=None):
        if options is None:
            options = {}
        options.setdefault("query_cls", UserScopedQuery)
        return scoped_session(sessionmaker(**options))


ma = Marshmallow()
db = SQLAlchemy()
jwt = JWTManager()
celery = make_celery()
