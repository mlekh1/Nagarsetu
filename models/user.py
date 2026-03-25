from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    mobile = Column(String, unique=True, nullable=False)
    role = Column(String, default="citizen")
    is_approved = Column(Boolean, default=False)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    city = Column(String, nullable=True)