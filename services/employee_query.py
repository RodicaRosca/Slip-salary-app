from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.models import Employee, User, Role
from typing import List


def get_all_managers_service(session: Session) -> List[Employee]:
    try:
        managers = (
            session.query(Employee)
            .join(User, Employee.user_id == User.id)
            .join(Role, User.role_id == Role.id)
            .filter(Role.name == 'manager')
            .all()
        )
        return managers
    except Exception as e:
        print(f"Error retrieving managers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving managers.")


def get_all_employees_service(session: Session) -> List[Employee]:
    try:
        employees = (
            session.query(Employee)
            .join(User, Employee.user_id == User.id)
            .join(Role, User.role_id == Role.id)
            .filter(Role.name == 'employee')
            .all()
        )
        return employees
    except Exception as e:
        print(f"Error retrieving employees: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving employees.")
