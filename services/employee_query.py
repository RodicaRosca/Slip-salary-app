from sqlalchemy.orm import Session
from models.models import Employee, User, Role
from typing import List

def get_all_managers_service(session: Session) -> List[Employee]:
    # Get all users with role 'manager' and their employee records
    managers = (
        session.query(Employee)
        .join(User, Employee.user_id == User.id)
        .join(Role, User.role_id == Role.id)
        .filter(Role.name == 'manager')
        .all()
    )
    return managers


def get_all_employees_service(session: Session) -> List[Employee]:
    # Get all users with role 'employee' and their employee records
    employees = (
        session.query(Employee)
        .join(User, Employee.user_id == User.id)
        .join(Role, User.role_id == Role.id)
        .filter(Role.name == 'employee')
        .all()
    )
    return employees
