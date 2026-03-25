from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from models.user import User
from models.ward import Ward
from schemas.user import RegisterRequest, OTPVerifyRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

# Temporary OTP store (in memory for hackathon)
otp_store = {}

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(User).filter(User.mobile == data.mobile).first()
    if existing:
        raise HTTPException(status_code=400, detail="Mobile already registered")

    # Auto detect ward using GPS coordinates
    point = f"SRID=4326;POINT({data.longitude} {data.latitude})"
    ward = db.query(Ward).filter(
        Ward.polygon.ST_Contains(f"SRID=4326;POINT({data.longitude} {data.latitude})")
    ).first()

    # Create user
    user = User(
        mobile=data.mobile,
        name=data.name,
        ward_id=ward.id if ward else None,
        city=ward.city if ward else None,
        is_approved=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Mock OTP — always 123456 for hackathon
    otp_store[data.mobile] = "123456"

    return {
        "message": "OTP sent successfully",
        "otp": "123456",  # Remove this in production!
        "ward_detected": ward.name if ward else "No ward found"
    }

@router.post("/verify-otp")
def verify_otp(data: OTPVerifyRequest, db: Session = Depends(get_db)):
    # Check OTP
    if otp_store.get(data.mobile) != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Get user
    user = db.query(User).filter(User.mobile == data.mobile).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Clear OTP
    otp_store.pop(data.mobile)

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "mobile": user.mobile,
            "role": user.role,
            "ward_id": user.ward_id,
            "city": user.city,
            "is_approved": user.is_approved
        }
    }
@router.put("/approve-user/{user_id}")
def approve_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_approved = True
    db.commit()
    return {"message": f"User {user.name} approved successfully"}
@router.get("/pending-users/{ward_id}")
def get_pending_users(ward_id: int, db: Session = Depends(get_db)):
    users = db.query(User).filter(
        User.ward_id == ward_id,
        User.is_approved == False
    ).all()
    return users