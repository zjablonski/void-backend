from flask import Blueprint, g
from flask_jwt_extended import jwt_required, get_jwt_identity

from db.models import User
from db.schemas import UserSchema
from dotenv import load_dotenv

load_dotenv()
user_bp = Blueprint("user_bp", __name__)


@user_bp.before_request
@jwt_required()
def require_jwt():
    g.user_id = get_jwt_identity()


@user_bp.route("/", methods=["GET"])
@jwt_required()
def get_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    return UserSchema().dump(user), 200
