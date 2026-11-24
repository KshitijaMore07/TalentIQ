import smtplib
from email.message import EmailMessage
from config import Config
from ..extensions import db
from ..models import Notification


def notify(user, message, subject="TalentIQ update", to_email=None):
    """Store an in-app notification and send an email when SMTP is configured."""
    if user:
        db.session.add(Notification(user_id=user.id, message=message[:400]))
    addr = to_email or (user.email if user else None)
    if not addr:
        return
    if not Config.SMTP_HOST:
        print(f"[notify] (SMTP not configured) to {addr}: {message}")
        return
    try:
        m = EmailMessage(); m["Subject"], m["From"], m["To"] = subject, Config.SMTP_USER, addr
        m.set_content(message)
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10) as s:
            s.starttls(); s.login(Config.SMTP_USER, Config.SMTP_PASSWORD); s.send_message(m)
    except Exception as e:
        print("[notify] email failed:", e)
