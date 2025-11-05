import os
from datetime import datetime
from models.models import Employee
from services.employee_report import generate_employee_salary_report

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