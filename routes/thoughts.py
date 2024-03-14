from flask import request, Blueprint, g
from flask_jwt_extended import jwt_required, get_jwt_identity

from db.models import Thought
from db.schemas import ThoughtsSchema
from dotenv import load_dotenv
from utils.extensions import db

load_dotenv()
thoughts_bp = Blueprint("thought_bp", __name__)


@thoughts_bp.before_request
@jwt_required()
def require_jwt():
    g.user_id = get_jwt_identity()


# Create
@thoughts_bp.route("/", methods=["POST"])
def create_thought():
    thought = ThoughtsSchema().load(request.json)
    thought.is_active = True
    thought.user_id = g.user_id

    db.session.add(thought)
    db.session.commit()
    return ThoughtsSchema().dump(thought), 201


# Update
@thoughts_bp.route("/<int:thought_id>", methods=["PUT"])
def update_thought(thought_id):
    thought = Thought.get_or_404(thought_id)
    thought = ThoughtsSchema().load(request.json, instance=thought)
    db.session.commit()
    return ThoughtsSchema().dump(thought)


# Delete
@thoughts_bp.route("/<int:thought_id>", methods=["DELETE"])
def delete_thought(thought_id):
    thought = Thought.get_or_404(thought_id)
    db.session.delete(thought)
    db.session.commit()
    return "", 204
