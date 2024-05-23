from dotenv import load_dotenv
from flask import Blueprint, g, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from db.models import Category, Thing, ThingStatus
from db.schemas import ThingListSchema, ThingSchema
from utils.extensions import db


load_dotenv()
thing_bp = Blueprint("thing_bp", __name__)


@thing_bp.before_request
@jwt_required()
def require_jwt():
    g.user_id = get_jwt_identity()


@thing_bp.route("/", methods=["POST"])
def create_thing():
    thing = ThingListSchema().load(request.json)
    thing.status = ThingStatus.APPROVED.value
    thing.category = Category.Other.value
    thing.user_id = g.user_id

    db.session.add(thing)
    db.session.commit()
    return ThingListSchema().dump(thing), 201


@thing_bp.route("/<int:thing_id>", methods=["GET"])
def get_thing(thing_id):
    thing = Thing.get_or_404(thing_id)
    return ThingSchema().dump(thing)


@thing_bp.route("/", methods=["GET"])
def get_things():
    all_things = Thing.all()
    return ThingListSchema(many=True).dump(all_things)


@thing_bp.route("/<int:thing_id>", methods=["PUT"])
def update_thing(thing_id):
    thing = Thing.get_or_404(thing_id)
    thing = ThingListSchema().load(request.json, instance=thing)
    db.session.commit()
    return ThingListSchema().dump(thing)


@thing_bp.route("/<int:thing_id>", methods=["DELETE"])
def delete_thing(thing_id):
    thing = Thing.get_or_404(thing_id)
    db.session.delete(thing)
    db.session.commit()
    return "", 204
