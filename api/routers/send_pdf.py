
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.session import SessionLocal
from services.pdf_generator import generate_salary_pdf
from models.models import Employee
import smtplib
from email.message import EmailMessage
import os
from datetime import datetime
from core.auth import manager_required
import traceback

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.post("/sendPdfToEmployees")
def send_pdf_to_employees(db: Session = Depends(get_db), current_user=Depends(manager_required)):
    employees = db.query(Employee).all()
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found.")

    smtp_server = os.getenv("SMTP_SERVER", "smtp.example.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER", "user@example.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "password")
    sender_email = os.getenv("SENDER_EMAIL", smtp_user)

    sent_count = 0
    errors = []
    archive_dir = os.path.join(os.getcwd(), "archive")
    os.makedirs(archive_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for emp in employees:
        try:
            pdf_bytes = generate_salary_pdf(db, emp.id)
            # Archive the PDF
            archive_path = os.path.join(archive_dir, f"salary_slip_{emp.employee_id}_{timestamp}.pdf")
            with open(archive_path, "wb") as f:
                f.write(pdf_bytes)

            msg = EmailMessage()
            msg["Subject"] = "Your Salary Slip"
            msg["From"] = sender_email
            msg["To"] = emp.email
            msg.set_content(f"Dear {emp.first_name},\n\nPlease find attached your salary slip for this month.\n\nBest regards,\nHR Department")
            msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename=f"salary_slip_{emp.employee_id}.pdf")

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            sent_count += 1
        except Exception as e:
            print(f"Error sending email to {emp.email}: {e}")
            traceback.print_exc()
            errors.append({"employee": emp.email, "error": str(e)})
            continue
    return {"sent": sent_count, "total": len(employees), "errors": errors}
