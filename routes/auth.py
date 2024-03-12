from flask import request, Blueprint, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from models import Thought, User
from schemas import ThoughtsSchema
from dotenv import load_dotenv
from utils.extensions import db


load_dotenv()
auth_bp = Blueprint("auth_bp", __name__)


# Create
@auth_bp.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if not email or not password:
        return jsonify({"msg": "Username and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"msg": "Email already taken"}), 400

    user = User(email=email.lower())
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id), expires_delta=False)
    return jsonify(access_token=access_token)


@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=email.lower()).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id), expires_delta=False)
        return jsonify(access_token=access_token)

    return jsonify({"msg": "Bad username or password"}), 401


@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
