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


class Transcription(db.Model):
    __tablename__ = 'transcriptions'
    id = Column(Integer, primary_key=True)
    assemblyai_id = Column(Text)

    status = Column(String(64))
    text = Column(Text)
    file_name = Column(Text)

    shallow_analysis = Column(JSON)
    deep_analysis = Column(JSON)

    created_at = Column(DateTime, default=func.now())


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
    notes = Column(Text)
    raw_text = Column(Text)

    occurred_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

    thing_id = Column(Integer, ForeignKey('things.id'))
    thing = relationship('Thing', back_populates='events')


class Thoughts(db.Model):
    __tablename__ = "thoughts"

    id = Column(Integer, primary_key=True)
    text = Column(Text, unique=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"id: {self.id}, text: {self.text}"