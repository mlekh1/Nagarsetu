from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.complaint import Complaint, TicketStatus
from models.user import User
from schemas.complaint import ComplaintCreate, ComplaintResponse
import random, string
from datetime import datetime

router = APIRouter(prefix="/complaints", tags=["Complaints"])

def generate_ticket_id():
    year = datetime.now().year
    random_part = ''.join(random.choices(string.digits, k=5))
    return f"NS-{year}-{random_part}"

@router.post("/", response_model=ComplaintResponse)
def raise_complaint(data: ComplaintCreate, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="Your account is pending ward head approval")
    if not user.ward_id:
        raise HTTPException(status_code=400, detail="User ward not detected. Please re-register with valid location.")

    complaint = Complaint(
        ticket_id=generate_ticket_id(),
        user_id=user.id,
        ward_id=user.ward_id,
        department=data.department,
        description=data.description,
        latitude=data.latitude,
        longitude=data.longitude,
        image_url=data.image_url,
        status=TicketStatus.open
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint

@router.get("/my-tickets", response_model=list[ComplaintResponse])
def get_my_tickets(user_id: int, db: Session = Depends(get_db)):
    return db.query(Complaint).filter(Complaint.user_id == user_id).all()

@router.get("/ward/{ward_id}", response_model=list[ComplaintResponse])
def get_ward_complaints(ward_id: int, db: Session = Depends(get_db)):
    return db.query(Complaint).filter(Complaint.ward_id == ward_id).all()

@router.put("/{ticket_id}/remark")
def add_remark(ticket_id: str, remark: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.ticket_id == ticket_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Ticket not found")
    complaint.worker_remark = remark
    complaint.status = TicketStatus.in_progress
    db.commit()
    return {"message": "Remark added", "ticket_id": ticket_id}

@router.put("/{ticket_id}/close")
def close_ticket(ticket_id: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.ticket_id == ticket_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Ticket not found")
    complaint.status = TicketStatus.resolved
    db.commit()
    return {"message": "Ticket closed", "ticket_id": ticket_id}