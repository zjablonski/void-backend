from sqlalchemy import Column, DateTime, String, Integer, func, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from enum import Enum
from utils.extensions import db


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Category(ExtendedEnum):
    Other = 'Other'
    Health = 'Health'
    Exercise = 'Exercise'
    Mood = 'Mood'


class AudioLog(db.Model):
    __tablename__ = 'audio_logs'
    id = Column(Integer, primary_key=True)
    assemblyai_id = Column(Text)

    status = Column(String(64))
    file_name = Column(Text)
    text = Column(Text)

    # Data generated from LLMs
    identified_things = Column(JSON)
    raw_events = Column(JSON)
    raw_thoughts = Column(JSON)
    raw_shallow_analysis = Column(JSON)
    raw_deep_analysis = Column(JSON)
    system_notes = Column(Text, default="")  # used to store issues w/ processing

    created_at = Column(DateTime, default=func.now())

    events = relationship('Event', back_populates='audio_log')
    thoughts = relationship('Thought', back_populates='audio_log')


class Thing(db.Model):
    __tablename__ = "things"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True)
    category = Column(String(200))
    unit = Column(String(64), nullable=True)

    events = relationship('Event', back_populates='thing')

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"


class Event(db.Model):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    amount = Column(String(64))
    note = Column(Text)

    occurred_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

    audio_log = relationship('AudioLog', back_populates='events')
    audio_log_id = Column(Integer, ForeignKey('audio_logs.id'))

    thing = relationship('Thing', back_populates='events')
    thing_id = Column(Integer, ForeignKey('things.id'))


class Thought(db.Model):
    __tablename__ = "thoughts"

    id = Column(Integer, primary_key=True)
    text = Column(Text)

    created_at = Column(DateTime, default=func.now())

    audio_log = relationship('AudioLog', back_populates='thoughts')
    audio_log_id = Column(Integer, ForeignKey('audio_logs.id'))

    def __repr__(self):
        return f"id: {self.id}, text: {self.text}"