from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from services.salary_slip_create import create_salary_slip_service, get_salary_slips_for_employee
from api.salary_schemas import SalarySlipCreate
from core.auth import manager_required, get_db  


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
        return get_salary_slips_for_employee(db, employee_id)
    except Exception as e:
        print(f"Error listing salary slips for employee {employee_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error while listing salary slips.")