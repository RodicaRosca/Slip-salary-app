from fastapi import APIRouter, Response, HTTPException, Depends
from db.session import SessionLocal
from services.employee_report import generate_employee_salary_report
from services.employee_create import create_employee_service
from services.employee_query import get_all_employees_service, get_all_managers_service
from api.schemas import EmployeeCreate
from fastapi.encoders import jsonable_encoder

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.get("/")
async def read_root():
    return {"Hello": "World"}

@router.get("/createAggregatedEmployeeData")
def create_aggregated_employee_data(db=Depends(get_db)):
    excel_bytes = generate_employee_salary_report(db)
    headers = {
        'Content-Disposition': 'attachment; filename="aggregated_employee_data.xlsx"'
    }
    return Response(content=excel_bytes, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)

@router.post("/createEmployee")
def create_employee(emp: EmployeeCreate, db=Depends(get_db)):
    try:
        result = create_employee_service(db, emp)
        return result
    except HTTPException as e:
        raise e
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.get("/managers")
def get_managers(db=Depends(get_db)):
    managers = get_all_managers_service(db)
    return jsonable_encoder(managers)

@router.get("/employees")
def get_employees(db=Depends(get_db)):
    employees = get_all_employees_service(db)
    return jsonable_encoder(employees)
