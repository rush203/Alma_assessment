
import os
import smtplib
from email.message import EmailMessage
from jinja2 import Template
from pathlib import Path
from app.config import settings

def _render(template: str, **ctx) -> str:
    return Template(template).render(**ctx)

PROSPECT_TEMPLATE = """
Hi {{ first_name }},

Thanks for contacting us! We've received your information and will reach out shortly.

Best,
Acme Law
"""

ATTORNEY_TEMPLATE = """
New lead submitted:

Name: {{ first_name }} {{ last_name }}
Email: {{ email }}
Lead ID: {{ lead_id }}
Resume: {{ resume_path }}

View Lead API: {{ base_url }}/leads/{{ lead_id }}
"""

def _send_smtp(subject: str, to_email: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USERNAME:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD or "")
        server.send_message(msg)

def _send_console(subject: str, to_email: str, body: str):
    outdir = Path(settings.OUTBOX_DIR)
    outdir.mkdir(parents=True, exist_ok=True)
    filename = outdir / f"{to_email.replace('@','_at_')}_{subject.replace(' ','_')}.eml"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Subject: {subject}\n")
        f.write(f"From: {settings.FROM_EMAIL}\n")
        f.write(f"To: {to_email}\n\n")
        f.write(body)

def send_email(subject: str, to_email: str, body: str):
    backend = settings.MAILER_BACKEND.lower()
    if backend == "smtp":
        _send_smtp(subject, to_email, body)
    else:
        _send_console(subject, to_email, body)

def send_prospect_email(first_name: str, email: str):
    body = _render(PROSPECT_TEMPLATE, first_name=first_name)
    send_email("We've received your information", email, body)

def send_attorney_email(first_name: str, last_name: str, email: str, lead_id: str, resume_path: str):
    body = _render(ATTORNEY_TEMPLATE, first_name=first_name, last_name=last_name, email=email, lead_id=lead_id, resume_path=resume_path, base_url=settings.BASE_URL)
    send_email("New Lead Submitted", settings.ATTORNEY_EMAIL, body)
