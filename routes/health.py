from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.complaint import Complaint, TicketStatus

router = APIRouter(prefix="/health", tags=["Ward Health"])

def calculate_health_score(ward_id: int, db: Session):
    all_complaints = db.query(Complaint).filter(Complaint.ward_id == ward_id).all()

    if not all_complaints:
        return {
            "score": 100,
            "color": "green",
            "total_complaints": 0,
            "open": 0,
            "in_progress": 0,
            "resolved": 0
        }

    total = len(all_complaints)
    open_count = len([c for c in all_complaints if c.status == TicketStatus.open])
    in_progress = len([c for c in all_complaints if c.status == TicketStatus.in_progress])
    resolved = len([c for c in all_complaints if c.status == TicketStatus.resolved])

    # Resolution rate (30 points)
    resolution_rate = (resolved / total) * 30

    # Response rate — tickets that got a remark (25 points)
    remarked = len([c for c in all_complaints if c.worker_remark is not None])
    response_score = (remarked / total) * 25

    # Penalty for open tickets sitting unattended (25 points deducted)
    open_penalty = (open_count / total) * 25

    # Base score starts at 45 (feedback score placeholder = 20 pts assumed neutral)
    score = 45 + resolution_rate + response_score - open_penalty

    # Clamp between 0 and 100
    score = max(0, min(100, round(score)))

    # Color band
    if score >= 70:
        color = "green"
    elif score >= 40:
        color = "yellow"
    else:
        color = "red"

    return {
        "score": score,
        "color": color,
        "total_complaints": total,
        "open": open_count,
        "in_progress": in_progress,
        "resolved": resolved
    }

@router.get("/{ward_id}")
def get_ward_health(ward_id: int, db: Session = Depends(get_db)):
    result = calculate_health_score(ward_id, db)
    return {
        "ward_id": ward_id,
        **result
    }

@router.get("/city/all")
def get_all_wards_health(db: Session = Depends(get_db)):
    # Get all unique ward IDs that have complaints
    ward_ids = db.query(Complaint.ward_id).distinct().all()
    ward_ids = [w[0] for w in ward_ids if w[0] is not None]

    results = []
    for ward_id in ward_ids:
        health = calculate_health_score(ward_id, db)
        results.append({"ward_id": ward_id, **health})

    return results