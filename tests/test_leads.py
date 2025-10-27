
import os
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def auth_token():
    r = client.post("/auth/token", data={"username": settings.ATTORNEY_EMAIL, "password": "secret"})
    assert r.status_code == 200
    return r.json()["access_token"]

def test_public_create_and_list_flow():
    # create a temp resume file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4 test pdf")
        resume_path = f.name

    with open(resume_path, "rb") as f:
        r = client.post("/public/leads", files={"resume": ("resume.pdf", f, "application/pdf")}, data={
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@example.com"
        })
    assert r.status_code == 200, r.text
    lead = r.json()
    assert lead["state"] == "PENDING"
    assert lead["first_name"] == "John"

    token = auth_token()
    r = client.get("/leads", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert any(l["id"] == lead["id"] for l in data)

    # Update state
    r = client.patch(f"/leads/{lead['id']}/state", headers={"Authorization": f"Bearer {token}"}, json={"state":"REACHED_OUT"})
    assert r.status_code == 200
    assert r.json()["state"] == "REACHED_OUT"
