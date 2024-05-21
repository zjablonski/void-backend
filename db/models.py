import uuid
from enum import Enum
from flask import abort, g
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from utils.extensions import db


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Category(ExtendedEnum):
    Other = "Other"
    Health = "Health"
    Exercise = "Exercise"
    Mood = "Mood"


class ThingStatus(ExtendedEnum):
    SUGGESTED = "SUGGESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class AudioLogStatus(ExtendedEnum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TimestampedModel(db.Model):
    __abstract__ = True
    created_at = Column(DateTime, default=func.timezone("UTC", func.now()))
    updated_at = Column(
        DateTime,
        default=func.timezone("UTC", func.now()),
        onupdate=func.timezone("UTC", func.now()),
    )


class TimestampedUserModel(TimestampedModel):
    __abstract__ = True
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    @classmethod
    def get_or_404(cls, id):
        current_user_id = g.get("user_id", None)
        obj = cls.query.get_or_404(id)
        if current_user_id is None or str(obj.user_id) != str(current_user_id):
            abort(404, description="Resource not found or not owned.")
        else:
            return obj

    @classmethod
    def all(cls):
        current_user_id = g.get("user_id", None)
        return (
            cls.query.filter_by(user_id=current_user_id).all()
            if current_user_id
            else []
        )


class User(TimestampedModel):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(512))

    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    thoughts = relationship(
        "Thought", back_populates="user", cascade="all, delete-orphan"
    )
    logs = relationship("AudioLog", back_populates="user", cascade="all, delete-orphan")
    things = relationship("Thing", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class AudioLog(TimestampedUserModel):
    __tablename__ = "audio_logs"
    id = Column(Integer, primary_key=True)
    assemblyai_id = Column(Text)

    status = Column(String(64), default=AudioLogStatus.PENDING_APPROVAL.value)
    file_name = Column(Text)
    text = Column(Text)

    is_processing_complete = Column(Boolean, default=False)

    # Data generated from LLMs
    identified_things = Column(JSON)
    raw_shallow_analysis = Column(JSON)
    raw_deep_analysis = Column(JSON)
    system_notes = Column(Text, default="")  # used to store issues w/ processing

    events = relationship(
        "Event", back_populates="audio_log", cascade="all, delete-orphan"
    )
    thoughts = relationship(
        "Thought", back_populates="audio_log", cascade="all, delete-orphan"
    )

    user = relationship("User", back_populates="logs")


class Thing(TimestampedUserModel):
    __tablename__ = "things"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True)
    category = Column(String(200))
    unit = Column(String(64), nullable=True)

    status = Column(String, default=ThingStatus.SUGGESTED.value)

    events = relationship("Event", back_populates="thing")

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="things")

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"


class Event(TimestampedUserModel):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    amount = Column(String(64))
    note = Column(Text)
    is_active = Column(Boolean, default=False)  # inactive until confirmed by user

    occurred_at = Column(
        DateTime, default=func.timezone("UTC", func.timezone("UTC", func.now()))
    )

    audio_log = relationship("AudioLog", back_populates="events")
    audio_log_id = Column(Integer, ForeignKey("audio_logs.id"))

    thing = relationship("Thing", back_populates="events")
    thing_id = Column(Integer, ForeignKey("things.id"))

    user = relationship("User", back_populates="events")


class Thought(TimestampedUserModel):
    __tablename__ = "thoughts"

    id = db.Column(db.Integer, primary_key=True)
    text = Column(Text)
    is_active = Column(Boolean, default=False)  # inactive until confirmed by user

    audio_log = relationship("AudioLog", back_populates="thoughts")
    audio_log_id = Column(Integer, ForeignKey("audio_logs.id"))

    user = relationship("User", back_populates="thoughts")

    def __repr__(self):
        return f"id: {self.id}, text: {self.text}"
