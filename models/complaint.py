from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class DepartmentType(str, enum.Enum):
    water = "water"
    electricity = "electricity"
    cleanliness = "cleanliness"
    infrastructure = "infrastructure"
    others = "others"

class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True)  # e.g. NS-2024-00042
    user_id = Column(Integer, ForeignKey("users.id"))
    ward_id = Column(Integer, ForeignKey("wards.id"))
    department = Column(Enum(DepartmentType))
    description = Column(String)
    status = Column(Enum(TicketStatus), default=TicketStatus.open)
    latitude = Column(Float)
    longitude = Column(Float)
    image_url = Column(String, nullable=True)
    worker_remark = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())