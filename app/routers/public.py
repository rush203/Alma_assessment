
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import LeadOut, LeadCreate
from app.services.lead_service import save_resume, create_lead
from app.emailer import send_prospect_email, send_attorney_email

router = APIRouter(prefix="/public", tags=["public"])

@router.post("/leads", response_model=LeadOut, summary="Create a lead (public)")
async def create_public_lead(
    background_tasks: BackgroundTasks,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    resume_path = save_resume(resume)
    lead = create_lead(db, first_name=first_name, last_name=last_name, email=email, resume_path=resume_path)

    # Background emails
    background_tasks.add_task(send_prospect_email, first_name, email)
    background_tasks.add_task(send_attorney_email, first_name, last_name, email, lead.id, resume_path)

    return lead
