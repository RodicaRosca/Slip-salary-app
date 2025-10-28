from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    users = relationship('User', back_populates='role')

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    role = relationship('Role', back_populates='users')
    employee = relationship('Employee', back_populates='user', uselist=False, foreign_keys='Employee.user_id')
    managed_employees = relationship('Employee', back_populates='manager', foreign_keys='Employee.manager_id')

class Employee(Base):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    cnp = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(String(255))
    date_of_birth = Column(Date)
    hire_date = Column(Date)
    position = Column(String(100))
    department = Column(String(100))
    iban = Column(String(34))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey('user.id'))
    manager_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User', back_populates='employee', foreign_keys=[user_id])
    manager = relationship('User', back_populates='managed_employees', foreign_keys=[manager_id])
    salary_slips = relationship('SalarySlip', back_populates='employee')

class SalarySlip(Base):
    __tablename__ = 'salary_slip'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employee.id', ondelete='CASCADE'))
    month = Column(Date, nullable=False)
    base_salary = Column(Numeric(12, 2), nullable=False)
    working_days = Column(Integer, nullable=False)
    vacation_days = Column(Integer, nullable=False)
    bonuses = Column(Numeric(12, 2), default=0)
    total_salary = Column(Numeric(12, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    employee = relationship('Employee', back_populates='salary_slips')
