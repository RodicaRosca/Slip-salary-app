from fastapi import APIRouter,  HTTPException, Depends
from core.auth import manager_required, get_db
from services.employee_create import create_employee_service
from services.employee_query import get_all_employees_service, get_all_managers_service
from api.schemas import EmployeeCreate
from fastapi.encoders import jsonable_encoder
from models.models import User
from sqlalchemy.orm import Session


router = APIRouter()


@router.get("/")
async def read_root(current_user=Depends(manager_required)):
    return {"Hello": "World"}


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