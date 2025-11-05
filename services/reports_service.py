import os
import smtplib
import traceback
from datetime import datetime
from models.models import Employee
from services.employee_report import generate_employee_salary_report
from services.pdf_generator import generate_salary_pdf
from email.message import EmailMessage
from fastapi import HTTPException

smtp_server = os.getenv("SMTP_SERVER", "smtp.example.com")
smtp_port = int(os.getenv("SMTP_PORT", 587))
smtp_user = os.getenv("SMTP_USER", "user@example.com")
smtp_password = os.getenv("SMTP_PASSWORD", "password")
sender_email = os.getenv("SENDER_EMAIL", smtp_user)

def create_manager_report(db, manager_id):
    archive_dir = os.path.join(os.getcwd(), "archive")
    os.makedirs(archive_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    employees = db.query(Employee).filter(Employee.manager_id == manager_id).all()
    if not employees:
        return {"sent": 0, "errors": ["No employees found for this manager."]}

    excel_bytes = generate_employee_salary_report(db, employees=employees)
    archive_path = os.path.join(archive_dir, f"salary_report_{timestamp}.xlsx")
    with open(archive_path, "wb") as f:
        f.write(excel_bytes)

    return {"sent": 1, "errors": []}



def create_pdfs_for_employees(db, manager_id):
    archive_dir = os.path.join(os.getcwd(), "archive")
    os.makedirs(archive_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    employees = db.query(Employee).filter(Employee.manager_id == manager_id).all()
    if not employees:
        return {"generated": False, "error": f"No employees found for manager_id {manager_id}", "manager_id": manager_id}

    generated = []
    errors = []
    for emp in employees:
        try:
            pdf_bytes = generate_salary_pdf(db, emp.id)
            archive_path = os.path.join(archive_dir, f"salary_slip_{emp.employee_id}_{timestamp}.pdf")
            with open(archive_path, "wb") as f:
                f.write(pdf_bytes)
            generated.append({"employee": emp.email, "file": archive_path})
        except ValueError as e:
            errors.append({"employee": emp.email, "error": str(e)})
        except Exception as e:
            traceback.print_exc()
            errors.append({"employee": emp.email, "error": str(e)})
    return {"generated": generated, "errors": errors}


def get_latest_report_file(archive_dir, prefix, extension):
    os.makedirs(archive_dir, exist_ok=True)
    files = [f for f in os.listdir(archive_dir) if f.startswith(prefix) and f.endswith(extension)]
    if not files:
        return None
    latest_file = max(files, key=lambda x: x[len(prefix):-len(extension)])
    return os.path.join(archive_dir, latest_file)

def send_report_to_manager(manager_email):
    archive_dir = os.path.join(os.getcwd(), "archive")
    prefix = "salary_report_"
    extension = ".xlsx"
    excel_path = get_latest_report_file(archive_dir, prefix, extension)
    if not excel_path:
        return {"sent": 0, "errors": ["No archived Excel report found."]}


    errors = []
    try:
        with open(excel_path, "rb") as f:
            excel_bytes = f.read()

        msg = EmailMessage()
        msg["Subject"] = "Aggregated Employee Salary Report"
        msg["From"] = sender_email
        msg["To"] = manager_email
        msg.set_content("Dear Manager,\n\nPlease find attached the aggregated employee salary report for this month.\n\nBest regards,\nHR Department")
        msg.add_attachment(excel_bytes, maintype="application", subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=os.path.basename(excel_path))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return {"sent": 1, "errors": []}
    except Exception as e:
        traceback.print_exc()
        errors.append({"manager": manager_email, "error": str(e)})
        return {"sent": 0, "errors": errors}
    

def send_pdfs_to_employees(db, manager_id):
    employees = db.query(Employee).filter(Employee.manager_id == manager_id).all()
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found for this manager.")


    sent_count = 0
    errors = []
    archive_dir = os.path.join(os.getcwd(), "archive")


    for emp in employees:
        prefix = f"salary_slip_{emp.employee_id}_"
        pdf_files = [f for f in os.listdir(archive_dir) if f.startswith(prefix) and f.endswith(".pdf")]
        if not pdf_files:
            errors.append({"employee": emp.email, "error": "No archived PDF found for this employee."})
            continue
        latest_pdf = max(pdf_files, key=lambda x: x[len(prefix):-4])  
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
