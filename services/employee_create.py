from sqlalchemy.orm import Session
from models.models import Employee, User, Role
from api.schemas import EmployeeCreate, RoleEnum
from fastapi import HTTPException
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_employee_service(session: Session, emp: EmployeeCreate):
    # Enforce that employees must have a manager_id, managers must not
    if emp.role == RoleEnum.employee and emp.manager_id is None:
        raise HTTPException(status_code=400, detail="manager_id is required for employees.")
    if emp.role == RoleEnum.manager and emp.manager_id is not None:
        raise HTTPException(status_code=400, detail="manager_id must not be set for managers.")

    # Get or create role
    role_obj = session.query(Role).filter_by(name=emp.role.value).first()
    if not role_obj:
        role_obj = Role(name=emp.role.value, description=f"{emp.role.value.title()} role")
        session.add(role_obj)
        session.commit()
        session.refresh(role_obj)

    # Hash the password
    hashed_password = hash_password(emp.password)

    # Create user
    user = User(
        username=emp.username,
        email=emp.email,
        password_hash=hashed_password,
        role_id=role_obj.id
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create employee
    employee = Employee(
        employee_id=f"EMP{user.id}",
        first_name=emp.first_name,
        last_name=emp.last_name,
        cnp=emp.cnp,
        email=emp.email,
        phone=emp.phone,
        address=emp.address,
        date_of_birth=emp.date_of_birth,
        hire_date=emp.hire_date,
        position=emp.position,
        department=emp.department,
        iban=emp.iban,
        user_id=user.id,
        manager_id=emp.manager_id
    )
    session.add(employee)
    session.commit()
    return {"message": "Employee created successfully", "employee_id": employee.employee_id}
