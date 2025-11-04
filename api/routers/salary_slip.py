from models.models import SalarySlip
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from db.session import SessionLocal
from services.salary_slip_create import create_salary_slip_service
from api.salary_schemas import SalarySlipCreate
from core.auth import manager_required


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.post("/createSalarySlip")
def create_salary_slip(slip: SalarySlipCreate, db=Depends(get_db), current_user=Depends(manager_required)):
    try:
        result = create_salary_slip_service(db, slip)
        return result
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error.")


@router.get("/salarySlips/{employee_id}")
def list_salary_slips(employee_id: int, db: Session = Depends(get_db), current_user=Depends(manager_required)):
    try:
        slips = db.query(SalarySlip).filter(SalarySlip.employee_id == employee_id).order_by(SalarySlip.month.desc()).all()
        return [
            {
                "id": slip.id,
                "employee_id": slip.employee_id,
                "month": slip.month,
                "base_salary": float(slip.base_salary),
                "working_days": slip.working_days,
                "vacation_days": slip.vacation_days,
                "bonuses": float(slip.bonuses),
                "total_salary": float(slip.total_salary),
                "created_at": slip.created_at
            }
            for slip in slips
        ]
    except Exception as e:
        print(f"Error listing salary slips for employee {employee_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error while listing salary slips.")