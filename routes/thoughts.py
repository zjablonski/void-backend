from dotenv import load_dotenv
from flask import Blueprint, g, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from db.models import Thought
from db.schemas import ThoughtSchema
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
    thought = ThoughtSchema().load(request.json)
    thought.is_active = True
    thought.user_id = g.user_id

    db.session.add(thought)
    db.session.commit()
    return ThoughtSchema().dump(thought), 201


# Update
@thoughts_bp.route("/<int:thought_id>", methods=["PUT"])
def update_thought(thought_id):
    thought = Thought.get_or_404(thought_id)
    thought = ThoughtSchema().load(request.json, instance=thought)
    db.session.commit()
    return ThoughtSchema().dump(thought)


# Delete
@thoughts_bp.route("/<int:thought_id>", methods=["DELETE"])
def delete_thought(thought_id):
    thought = Thought.get_or_404(thought_id)
    db.session.delete(thought)
    db.session.commit()
    return "", 204
