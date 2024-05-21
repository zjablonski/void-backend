from dotenv import load_dotenv
from flask import Blueprint, g, request
from flask_jwt_extended import get_jwt_identity, jwt_required


from db.models import Event
from db.schemas import EventSchema
from utils.extensions import db

load_dotenv()
events_bp = Blueprint("events_bp", __name__)


@events_bp.before_request
@jwt_required()
def require_jwt():
    g.user_id = get_jwt_identity()


# Create
@events_bp.route("/", methods=["POST"])
def create_event():
    event = EventSchema().load(request.json)
    event.is_active = True
    event.user_id = g.user_id
    db.session.add(event)
    db.session.commit()
    return EventSchema().dump(event), 201


# Update
@events_bp.route("/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    event = Event.get_or_404(event_id)
    event = EventSchema().load(request.json, instance=event)
    db.session.commit()
    return EventSchema().dump(event)


# Delete
@events_bp.route("/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = Event.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return "", 204
