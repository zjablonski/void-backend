from utils.extensions import ma
from models import Thing, Event, Thought, AudioLog


class ThingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Thing
        load_instance = True  # Optional: deserialize to model instances


class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        load_instance = True  # Optional: deserialize to model instances


class ThoughtsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Thought
        load_instance = True  # Optional: deserialize to model instances


class AudioLogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AudioLog
        load_instance = True  # Optional: deserialize to model instances