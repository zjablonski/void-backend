from flask import request, Blueprint, g
from flask_jwt_extended import jwt_required, get_jwt_identity

from db.models import Thing, ThingStatus, Category
from db.schemas import ThingListSchema, ThingSchema
from dotenv import load_dotenv
from utils.extensions import db

load_dotenv()
thing_bp = Blueprint("thing_bp", __name__)


@thing_bp.before_request
@jwt_required()
def require_jwt():
    g.user_id = get_jwt_identity()


# Create
@thing_bp.route("/", methods=["POST"])
def create_thing():
    thing = ThingListSchema().load(request.json)
    thing.status = ThingStatus.APPROVED.value
    thing.category = Category.Other.value
    thing.user_id = g.user_id

    db.session.add(thing)
    db.session.commit()
    return ThingListSchema().dump(thing), 201


# Read - single item
@thing_bp.route("/<int:thing_id>", methods=["GET"])
def get_thing(thing_id):
    thing = Thing.get_or_404(thing_id)
    return ThingSchema().dump(thing)


# Read - all items
@thing_bp.route("/", methods=["GET"])
def get_things():
    all_things = Thing.all()
    return ThingListSchema(many=True).dump(all_things)


# Update
@thing_bp.route("/<int:thing_id>", methods=["PUT"])
def update_thing(thing_id):
    thing = Thing.get_or_404(thing_id)
    thing = ThingListSchema().load(request.json, instance=thing)
    db.session.commit()
    return ThingListSchema().dump(thing)


# Delete
@thing_bp.route("/<int:thing_id>", methods=["DELETE"])
def delete_thing(thing_id):
    thing = Thing.get_or_404(thing_id)
    db.session.delete(thing)
    db.session.commit()
    return "", 204
