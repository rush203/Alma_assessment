
import os
import shutil
import uuid
from typing import BinaryIO
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.models import Lead, LeadState
from app.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}

def save_resume(file: UploadFile) -> str:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    uploads = Path(settings.UPLOAD_DIR)
    uploads.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    dest = uploads / filename
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    return str(dest)

def create_lead(db: Session, first_name: str, last_name: str, email: str, resume_path: str) -> Lead:
    lead = Lead(first_name=first_name, last_name=last_name, email=email, resume_path=resume_path, state=LeadState.PENDING)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

def update_lead_state(db: Session, lead: Lead, new_state: LeadState) -> Lead:
    # Allowed transitions: PENDING -> REACHED_OUT, REACHED_OUT -> REACHED_OUT (idempotent)
    if lead.state == LeadState.PENDING and new_state in (LeadState.PENDING, LeadState.REACHED_OUT):
        lead.state = new_state
    elif lead.state == LeadState.REACHED_OUT and new_state == LeadState.REACHED_OUT:
        pass  # idempotent
    else:
        raise HTTPException(status_code=400, detail=f"Invalid state transition: {lead.state.value} -> {new_state.value}")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead
