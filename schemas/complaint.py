from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime

class DepartmentType(str, Enum):
    water = "water"
    electricity = "electricity"
    cleanliness = "cleanliness"
    infrastructure = "infrastructure"
    others = "others"

class ComplaintCreate(BaseModel):
    department: DepartmentType
    description: str
    latitude: float
    longitude: float
    image_url: Optional[str] = None

class ComplaintResponse(BaseModel):
    id: int
    ticket_id: str
    department: DepartmentType
    description: str
    status: str
    latitude: float
    longitude: float
    ward_id: Optional[int]
    created_at: datetime
    worker_remark: Optional[str] = None

    class Config:
        from_attributes = True