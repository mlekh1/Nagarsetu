from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.complaint import Complaint, TicketStatus
from datetime import datetime, timedelta

router = APIRouter(prefix="/health", tags=["Ward Health"])

def calculate_ward_health(ward_id: int, db: Session):
    all_complaints = db.query(Complaint).filter(Complaint.ward_id == ward_id).all()

    if not all_complaints:
        return 100  # no complaints = perfect score

    total = len(all_complaints)

    # 1. Resolution rate (30 points)
    resolved = [c for c in all_complaints if c.status in [TicketStatus.resolved, TicketStatus.closed]]
    resolution_rate = (len(resolved) / total) * 30

    # 2. Response time score (25 points)
    # if worker remarked = good response, else bad
    remarked = [c for c in all_complaints if c.worker_remark is not None]
    response_score = (len(remarked) / total) * 25

    # 3. Severity penalty (25 points deducted)
    # complaints older than 8 hrs with no remark = severe
    cutoff = datetime.utcnow() - timedelta(hours=8)
    severe = [
        c for c in all_complaints
        if c.worker_remark is None
        and c.status == TicketStatus.open
        and c.created_at.replace(tzinfo=None) < cutoff
    ]
    severity_penalty = min((len(severe) / total) * 25, 25)

    # 4. Feedback placeholder (20 points) — full marks for now
    feedback_score = 20

    score = resolution_rate + response_score + feedback_score - severity_penalty
    return round(max(0, min(100, score)), 2)

def get_color(score):
    if score >= 70:
        return "green"
    elif score >= 40:
        return "yellow"
    else:
        return "red"

@router.get("/{ward_id}")
def ward_health(ward_id: int, db: Session = Depends(get_db)):
    score = calculate_ward_health(ward_id, db)
    return {
        "ward_id": ward_id,
        "health_score": score,
        "color": get_color(score),
        "label": "green = healthy, yellow = needs attention, red = critical"
    }

@router.get("/city/all")
def all_wards_health(db: Session = Depends(get_db)):
    from models.ward import Ward
    wards = db.query(Ward).all()
    result = []
    for ward in wards:
        score = calculate_ward_health(ward.id, db)
        result.append({
            "ward_id": ward.id,
            "ward_name": ward.name,
            "health_score": score,
            "color": get_color(score)
        })
    return result