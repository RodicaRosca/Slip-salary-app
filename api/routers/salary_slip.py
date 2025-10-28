from fastapi import APIRouter, HTTPException, Depends
from db.session import SessionLocal
from services.salary_slip_create import create_salary_slip_service
from api.salary_schemas import SalarySlipCreate

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.post("/createSalarySlip")
def create_salary_slip(slip: SalarySlipCreate, db=Depends(get_db)):
    try:
        result = create_salary_slip_service(db, slip)
        return result
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error.")
