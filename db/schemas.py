from db.models import AudioLog, Event, Thing, Thought, User
from utils.extensions import ma
from utils.s3_utils import generate_presigned_fetch_url


# TODO: Exclude sensitive fields from serialization


class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        include_fk = True
        load_instance = True


class ThingListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Thing
        load_instance = True


class ThingSchema(ma.SQLAlchemyAutoSchema):
    events = ma.Nested(EventSchema, many=True)

    class Meta:
        model = Thing
        load_instance = True


class ThoughtsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Thought
        include_fk = True
        load_instance = True


class AudioLogSchema(ma.SQLAlchemyAutoSchema):

    events = ma.Nested(EventSchema, many=True)
    thoughts = ma.Nested(ThoughtsSchema, many=True)

    audio_uri = ma.Method("get_audio_uri")

    def get_audio_uri(self, obj):
        return generate_presigned_fetch_url(obj.file_name)

    class Meta:
        model = AudioLog
        load_instance = True
        fields = (
            "id",
            "created_at",
            "status",
            "file_name",
            "is_processing_complete",
            "updated_at",
            "text",
            "identified_things",
            "events",
            "thoughts",
            "audio_uri",
        )


class AudioLogListSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = AudioLog
        load_instance = True
        fields = (
            "id",
            "created_at",
            "status",
            "file_name",
            "is_processing_complete",
            "updated_at",
            "text",
            "identified_things",
        )


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        # include_fk = True
        load_instance = True
        fields = ("id", "email")
