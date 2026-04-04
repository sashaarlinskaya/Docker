import os
import time
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional
import datetime

time.sleep(7)

DB_USER = os.getenv("DB_USER", "hruser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "hrpassword")
DB_HOST = os.getenv("DB_HOST", "postgres-service")
DB_NAME = os.getenv("DB_NAME", "hr_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    position = Column(String)
    department = Column(String)
    salary = Column(Float)
    hire_date = Column(Date)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="HR Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmployeeCreate(BaseModel):
    full_name: str
    position: str
    department: str
    salary: float
    hire_date: datetime.date


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = None
    hire_date: Optional[datetime.date] = None


@app.get("/employees")
def get_employees(
    skip: int = 0,
    limit: int = 50,
    department: Optional[str] = None,
    search: Optional[str] = None,
):
    db = SessionLocal()
    query = db.query(Employee)
    if department:
        query = query.filter(Employee.department == department)
    if search:
        query = query.filter(Employee.full_name.ilike(f"%{search}%"))
    total = query.count()
    employees = query.offset(skip).limit(limit).all()
    db.close()
    return {"total": total, "items": employees}


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    db = SessionLocal()
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    db.close()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@app.post("/employees")
def create_employee(emp: EmployeeCreate):
    db = SessionLocal()
    new_emp = Employee(**emp.dict())
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    db.close()
    return new_emp


@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, emp: EmployeeUpdate):
    db = SessionLocal()
    existing = db.query(Employee).filter(Employee.id == employee_id).first()
    if not existing:
        db.close()
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in emp.dict(exclude_none=True).items():
        setattr(existing, field, value)
    db.commit()
    db.refresh(existing)
    db.close()
    return existing


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    db = SessionLocal()
    existing = db.query(Employee).filter(Employee.id == employee_id).first()
    if not existing:
        db.close()
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(existing)
    db.commit()
    db.close()
    return {"detail": "Deleted"}


@app.get("/departments")
def get_departments():
    db = SessionLocal()
    departments = db.query(Employee.department).distinct().all()
    db.close()
    return [d[0] for d in departments]


@app.get("/stats/by-department")
def stats_by_department():
    db = SessionLocal()
    result = (
        db.query(
            Employee.department,
            func.count(Employee.id).label("count"),
            func.avg(Employee.salary).label("avg_salary"),
        )
        .group_by(Employee.department)
        .all()
    )
    db.close()
    return [
        {"department": r.department, "count": r.count, "avg_salary": round(r.avg_salary, 2)}
        for r in result
    ]


@app.get("/stats/salary-distribution")
def salary_distribution():
    db = SessionLocal()
    result = (
        db.query(Employee.position, func.avg(Employee.salary).label("avg_salary"))
        .group_by(Employee.position)
        .order_by(func.avg(Employee.salary).desc())
        .limit(15)
        .all()
    )
    db.close()
    return [{"position": r.position, "avg_salary": round(r.avg_salary, 2)} for r in result]


@app.get("/health")
def health():
    return {"status": "ok"}
