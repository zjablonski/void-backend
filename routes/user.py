from flask import request, Blueprint, jsonify, g
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from models import Thought, User
from schemas import ThoughtsSchema, UserSchema
from dotenv import load_dotenv
from utils.extensions import db


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
