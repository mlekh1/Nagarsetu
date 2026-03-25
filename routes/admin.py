from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.complaint import Complaint, TicketStatus
from models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])

# Ward head: see all pending users to approve
@router.get("/pending-users/{ward_id}")
def pending_users(ward_id: int, db: Session = Depends(get_db)):
    users = db.query(User).filter(
        User.ward_id == ward_id,
        User.is_approved == False
    ).all()
    return users

# Ward head: approve a user
@router.put("/approve-user/{user_id}")
def approve_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_approved = True
    db.commit()
    return {"message": f"User {user.name} approved"}

# Dept admin: see all complaints by department
@router.get("/complaints/{department}")
def complaints_by_dept(department: str, db: Session = Depends(get_db)):
    complaints = db.query(Complaint).filter(
        Complaint.department == department
    ).order_by(Complaint.created_at.desc()).all()
    return complaints

# Dept admin: see severity complaints (no remark after 8 hrs)
@router.get("/severity/{ward_id}")
def severity_complaints(ward_id: int, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(hours=8)
    severe = db.query(Complaint).filter(
        Complaint.ward_id == ward_id,
        Complaint.worker_remark == None,
        Complaint.status == TicketStatus.open,
        Complaint.created_at < cutoff
    ).all()
    return {
        "ward_id": ward_id,
        "severity_count": len(severe),
        "complaints": severe
    }

# Master admin: full city overview
@router.get("/city-overview")
def city_overview(db: Session = Depends(get_db)):
    total = db.query(Complaint).count()
    open_c = db.query(Complaint).filter(Complaint.status == TicketStatus.open).count()
    resolved = db.query(Complaint).filter(Complaint.status == TicketStatus.resolved).count()
    return {
        "total_complaints": total,
        "open": open_c,
        "resolved": resolved,
        "resolution_rate": f"{round((resolved/total)*100, 1)}%" if total > 0 else "N/A"
    }