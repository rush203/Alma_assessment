
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.config import settings
from app.database import Base, engine, SessionLocal
from app import models
from app.utils.security import get_password_hash
from app.auth import router as auth_router
from app.routers.public import router as public_router
from app.routers.leads import router as leads_router
from app.routers.files import router as files_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.on_event("startup")
def seed_user():
    # Seed a default attorney if not present
    db: Session = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == settings.ATTORNEY_EMAIL).first()
        if not user:
            user = models.User(
                email=settings.ATTORNEY_EMAIL,
                full_name="Default Attorney",
                hashed_password=get_password_hash("secret"),
            )
            db.add(user)
            db.commit()
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}

app.include_router(auth_router)
app.include_router(public_router)
app.include_router(leads_router)
app.include_router(files_router)
