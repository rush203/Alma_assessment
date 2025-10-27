
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.deps import require_attorney
from app.schemas import LeadOut, LeadUpdate
from app.models import Lead, LeadState
from app.services.lead_service import update_lead_state

router = APIRouter(prefix="/leads", tags=["leads"])

@router.get("", response_model=List[LeadOut], summary="List leads (internal)")
def list_leads(
    db: Session = Depends(get_db),
    _user=Depends(require_attorney),
    state: Optional[LeadState] = Query(None),
    q: Optional[str] = Query(None, description="Search by name/email contains"),
    skip: int = 0,
    limit: int = Query(50, le=200),
):
    query = db.query(Lead)
    if state:
        query = query.filter(Lead.state == state)
    if q:
        like = f"%{q}%"
        query = query.filter((Lead.first_name.ilike(like)) | (Lead.last_name.ilike(like)) | (Lead.email.ilike(like)))
    leads = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()
    return leads

@router.get("/{lead_id}", response_model=LeadOut, summary="Get a lead (internal)")
def get_lead(lead_id: str, db: Session = Depends(get_db), _user=Depends(require_attorney)):
    lead = db.query(Lead).get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.patch("/{lead_id}", response_model=LeadOut, summary="Update a lead (internal)")
def update_lead(lead_id: str, payload: LeadUpdate, db: Session = Depends(get_db), _user=Depends(require_attorney)):
    lead = db.query(Lead).get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if payload.notes is not None:
        lead.notes = payload.notes
    if payload.state is not None:
        lead = update_lead_state(db, lead, payload.state)
        return lead  # state update already committed
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.patch("/{lead_id}/state", response_model=LeadOut, summary="Update only lead state (internal)")
def update_lead_status(lead_id: str, payload: LeadUpdate, db: Session = Depends(get_db), _user=Depends(require_attorney)):
    if payload.state is None:
        raise HTTPException(status_code=400, detail="state is required")
    lead = db.query(Lead).get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead = update_lead_state(db, lead, payload.state)
    return lead
