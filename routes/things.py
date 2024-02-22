from flask import request, Blueprint

from models import Thing
from schemas import ThingSchema
from dotenv import load_dotenv
from utils.extensions import db

load_dotenv()
thing_bp = Blueprint('thing_bp', __name__)


# Create
@thing_bp.route('/thing', methods=['POST'])
def create_thing():
    thing = ThingSchema().load(request.json)
    db.session.add(thing)
    db.session.commit()
    return ThingSchema().dump(thing), 201


# Read - single item
@thing_bp.route('/thing/<int:thing_id>', methods=['GET'])
def get_thing(thing_id):
    thing = Thing.query.get_or_404(thing_id)
    return ThingSchema().dump(thing)


# Read - all items
@thing_bp.route('/things', methods=['GET'])
def get_things():
    all_things = Thing.query.all()
    return ThingSchema(many=True).dump(all_things)


# Update
@thing_bp.route('/thing/<int:thing_id>', methods=['PUT'])
def update_thing(thing_id):
    thing = Thing.query.get_or_404(thing_id)
    thing = ThingSchema().load(request.json, instance=thing)
    db.session.commit()
    return ThingSchema().dump(thing)


# Delete
@thing_bp.route('/thing/<int:thing_id>', methods=['DELETE'])
def delete_thing(thing_id):
    thing = Thing.query.get_or_404(thing_id)
    db.session.delete(thing)
    db.session.commit()
    return '', 204

