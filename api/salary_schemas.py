import datetime
from pydantic import BaseModel
from typing import Optional

class SalarySlipCreate(BaseModel):
    employee_id: int
    month: datetime.date
    base_salary: float
    working_days: int
    vacation_days: int
    bonuses: Optional[float] = 0.0
    total_salary: float
