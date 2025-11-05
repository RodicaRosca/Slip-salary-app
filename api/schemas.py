import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class RoleEnum(str, Enum):
    employee = 'employee'
    manager = 'manager'


class SalarySlipCreate(BaseModel):
    employee_id: int
    month: str
    base_salary: float
    working_days: int
    vacation_days: int
    bonuses: Optional[float] = 0.0


class SalarySlipResponse(BaseModel):
    id: int
    employee_id: int
    month: str
    base_salary: float
    working_days: int
    vacation_days: int
    bonuses: float
    total_salary: float
    created_at: str


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