import os
from datetime import datetime
from fastapi import APIRouter, Response, HTTPException, Depends
from core.auth import manager_required
from db.session import SessionLocal
from services.employee_report import generate_employee_salary_report
from services.employee_create import create_employee_service
from services.employee_query import get_all_employees_service, get_all_managers_service
from api.schemas import EmployeeCreate
from fastapi.encoders import jsonable_encoder
from models.models import User
from sqlalchemy.orm import Session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.get("/")
async def read_root(current_user=Depends(manager_required)):
    return {"Hello": "World"}


@router.get("/createAggregatedEmployeeData")
def create_aggregated_employee_data(db=Depends(get_db), current_user=Depends(manager_required)):
    excel_bytes = generate_employee_salary_report(db)
    # Archive the Excel file
    archive_dir = os.path.join(os.getcwd(), "archive")
    os.makedirs(archive_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = os.path.join(archive_dir, f"aggregated_employee_data_{timestamp}.xlsx")
    
    with open(archive_path, "wb") as f:
        f.write(excel_bytes)
    headers = {
        'Content-Disposition': 'attachment; filename="aggregated_employee_data.xlsx"'
    }

    return Response(content=excel_bytes, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)

@router.post("/createEmployee")
def create_employee(emp: EmployeeCreate, db=Depends(get_db), current_user=Depends(manager_required)):
    try:
        result = create_employee_service(db, emp)
        return result
    except HTTPException as e:
        raise e
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error.")


@router.get("/managers")
def get_managers(db=Depends(get_db), current_user=Depends(manager_required)):
    managers = get_all_managers_service(db)
    return jsonable_encoder(managers)

@router.get("/employees")
def get_employees(db=Depends(get_db), current_user=Depends(manager_required)):
    employees = get_all_employees_service(db)
    return jsonable_encoder(employees)


@router.get("/users", response_model=list[dict])
def list_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.name if user.role else None
        }
        for user in users
    ]