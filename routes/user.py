from dotenv import load_dotenv
from flask import Blueprint, g
from flask_jwt_extended import get_jwt_identity, jwt_required

from db.models import User
from db.schemas import UserSchema

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

    if not user:
        return "", 401

    return UserSchema().dump(user), 200
