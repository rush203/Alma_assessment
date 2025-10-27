
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from enum import Enum
from datetime import datetime
from app.models import LeadState

class LeadCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr

class LeadOut(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    resume_path: str
    state: LeadState
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LeadUpdate(BaseModel):
    # Allow notes update (optional) and state update (validated elsewhere)
    notes: Optional[str] = None
    state: Optional[LeadState] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None  # user email

class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True
