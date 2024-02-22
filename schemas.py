from utils.extensions import ma
from models import Thing, Event, Thoughts, Transcription


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
        model = Thoughts
        load_instance = True  # Optional: deserialize to model instances


class TranscriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transcription
        load_instance = True  # Optional: deserialize to model instances