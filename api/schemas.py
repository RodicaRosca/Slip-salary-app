import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class RoleEnum(str, Enum):
    employee = 'employee'
    manager = 'manager'


class EmployeeCreate(BaseModel):
    username: str
    password: str  
    email: EmailStr
    first_name: str
    last_name: str
    cnp: str
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: datetime.date
    hire_date: datetime.date
    position: Optional[str] = None
    department: Optional[str] = None
    iban: Optional[str] = None
    role: RoleEnum  
    manager_id: Optional[int] = None 