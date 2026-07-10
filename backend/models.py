import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from database import Base


class HCPProfile(Base):
    __tablename__ = "hcp_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    specialization = Column(String(255), default="")
    hospital = Column(String(255), default="")
    city = Column(String(255), default="")
    phone = Column(String(50), default="")
    email = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), nullable=False, index=True)
    interaction_type = Column(String(100), default="meeting")
    date = Column(String(50), default="")
    time = Column(String(50), default="")
    attendees = Column(Text, default="")
    topics_discussed = Column(Text, default="")
    sentiment = Column(String(50), default="neutral")
    materials_shared = Column(Text, default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
