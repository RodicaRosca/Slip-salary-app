import os
import smtplib
import traceback
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.models import Employee, User, Role
from email.message import EmailMessage
from datetime import datetime
from core.auth import manager_required
from core.idempotency import idempotency_key_dependency
from services.pdf_generator import generate_salary_pdf
from services.employee_report import generate_employee_salary_report


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.post("/createReportForManagers")
def create_report_for_managers(
    db: Session = Depends(get_db),
    current_user=Depends(manager_required),
    idempotency_key=Depends(idempotency_key_dependency)
):
    archive_dir = os.path.join(os.getcwd(), "archive")
    os.makedirs(archive_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        excel_bytes = generate_employee_salary_report(db)
        archive_path = os.path.join(archive_dir, f"salary_report_{timestamp}.xlsx")
        with open(archive_path, "wb") as f:
            f.write(excel_bytes)
        return {"generated": True, "file": archive_path}
    except Exception as e:
        print(f"Error generating Excel report: {e}")
        traceback.print_exc()
        return {"generated": False, "error": str(e)}
    

@router.post("/createPdfForEmployees")
def create_pdf_for_employees(
    db: Session = Depends(get_db),
    current_user=Depends(manager_required),
    idempotency_key=Depends(idempotency_key_dependency)
):
    employees = db.query(Employee).all()

    if not employees:
        raise HTTPException(status_code=404, detail="No employees found.")

    archive_dir = os.path.join(os.getcwd(), "archive")
    os.makedirs(archive_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    generated = []
    errors = []

    for emp in employees:
        try:
            pdf_bytes = generate_salary_pdf(db, emp.id)
            archive_path = os.path.join(archive_dir, f"salary_slip_{emp.employee_id}_{timestamp}.pdf")
            with open(archive_path, "wb") as f:
                f.write(pdf_bytes)
            generated.append({"employee": emp.email, "file": archive_path})
        except Exception as e:
            print(f"Error generating PDF for {emp.email}: {e}")
            traceback.print_exc()
            errors.append({"employee": emp.email, "error": str(e)})
            continue
    return {"generated": generated, "errors": errors}


router = APIRouter()
@router.post("/sendReportToManagers")
def send_report_to_managers(
    db: Session = Depends(get_db),
    current_user=Depends(manager_required),
    idempotency_key=Depends(idempotency_key_dependency)
):
    # Find all managers
    manager_role = db.query(Role).filter(Role.name == "manager").first()
    
    if not manager_role:
        raise HTTPException(status_code=404, detail="Manager role not found.")
    managers = db.query(User).filter(User.role_id == manager_role.id).all()
    if not managers:
        raise HTTPException(status_code=404, detail="No managers found.")

    # Find the latest Excel report in the archive
    archive_dir = os.path.join(os.getcwd(), "archive")
    os.makedirs(archive_dir, exist_ok=True)
    prefix = "salary_report_"
    excel_files = [f for f in os.listdir(archive_dir) if f.startswith(prefix) and f.endswith(".xlsx")]


    if not excel_files:
        return {"sent": 0, "total": 0, "errors": ["No archived Excel report found."]}
    latest_excel = max(excel_files, key=lambda x: x[len(prefix):-5])  # get the latest by timestamp
    excel_path = os.path.join(archive_dir, latest_excel)
    
    with open(excel_path, "rb") as f:
        excel_bytes = f.read()

    smtp_server = os.getenv("SMTP_SERVER", "smtp.example.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER", "user@example.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "password")
    sender_email = os.getenv("SENDER_EMAIL", smtp_user)

    sent_count = 0
    errors = []
    
    for manager in managers:
        try:
            msg = EmailMessage()
            msg["Subject"] = "Aggregated Employee Salary Report"
            msg["From"] = sender_email
            msg["To"] = manager.email
            msg.set_content("Dear Manager,\n\nPlease find attached the aggregated employee salary report for this month.\n\nBest regards,\nHR Department")
            msg.add_attachment(excel_bytes, maintype="application", subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=latest_excel)

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            sent_count += 1
        except Exception as e:
            print(f"Error sending report to {manager.email}: {e}")
            traceback.print_exc()
            errors.append({"manager": manager.email, "error": str(e)})
            continue
    return {"sent": sent_count, "total": len(managers), "errors": errors}


@router.post("/sendPdfToEmployees")
def send_pdf_to_employees(
    db: Session = Depends(get_db),
    current_user=Depends(manager_required),
    idempotency_key=Depends(idempotency_key_dependency)
):
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


    for emp in employees:
        # Find the latest PDF for this employee in the archive
        prefix = f"salary_slip_{emp.employee_id}_"
        pdf_files = [f for f in os.listdir(archive_dir) if f.startswith(prefix) and f.endswith(".pdf")]
        if not pdf_files:
            errors.append({"employee": emp.email, "error": "No archived PDF found for this employee."})
            continue
        latest_pdf = max(pdf_files, key=lambda x: x[len(prefix):-4])  # get the latest by timestamp
        pdf_path = os.path.join(archive_dir, latest_pdf)
        
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

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
