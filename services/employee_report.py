import pandas as pd
import io
from sqlalchemy.orm import Session
from models.models import Employee, SalarySlip
from datetime import date
from fastapi import HTTPException

def generate_employee_salary_report(session: Session, employees=None) -> bytes:
    try:
        today = date.today()
        month_start = today.replace(day=1)
        if employees is None:
            employees = session.query(Employee).all()
        data = []
        for emp in employees:
            slip = (
                session.query(SalarySlip)
                .filter(SalarySlip.employee_id == emp.id)
                .filter(SalarySlip.month >= month_start)
                .order_by(SalarySlip.month.desc())
                .first()
            )
            if slip:
                data.append({
                    "Employee name": f"{emp.first_name} {emp.last_name}",
                    "Salary to be paid": float(slip.total_salary),
                    "Working days": slip.working_days,
                    "Vacation days": slip.vacation_days,
                    "Bonuses": float(slip.bonuses or 0),
                })
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='SalaryData')
        output.seek(0)
        return output.read()
    except Exception as e:
        print(f"Error generating salary report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while generating salary report.")
