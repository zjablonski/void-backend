from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, String, Integer, func


Base = declarative_base()
metadata = Base.metadata

class Thing(Base):
    __tablename__ = "things"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True)
    # category = Column(Integer)
    note = Column(String(200))
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"