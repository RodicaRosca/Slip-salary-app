from sqlalchemy.orm import Session
from models.models import SalarySlip
from api.salary_schemas import SalarySlipCreate
from fastapi import HTTPException


def create_salary_slip_service(session: Session, slip: SalarySlipCreate):
    try:
        salary_slip = SalarySlip(
            employee_id=slip.employee_id,
            month=slip.month,
            base_salary=slip.base_salary,
            working_days=slip.working_days,
            vacation_days=slip.vacation_days,
            bonuses=slip.bonuses,
            total_salary=slip.total_salary
        )
        session.add(salary_slip)
        session.commit()
        session.refresh(salary_slip)
        return {"message": "Salary slip created successfully", "salary_slip_id": salary_slip.id}
    except Exception as e:
        print(f"Error creating salary slip: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while creating salary slip.")
