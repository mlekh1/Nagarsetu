from pydantic import BaseModel
from typing import Optional

class RegisterRequest(BaseModel):
    mobile: str
    name: str
    latitude: float
    longitude: float

class OTPVerifyRequest(BaseModel):
    mobile: str
    otp: str

class UserResponse(BaseModel):
    id: int
    name: str
    mobile: str
    role: str
    is_approved: bool
    ward_id: Optional[int]
    city: Optional[str]

    class Config:
        from_attributes = True