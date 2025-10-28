"""Department API routes following SOLID principles"""

from typing import List
from fastapi import APIRouter, HTTPException

from ..models.department import Department
from ..services.employee_service import EmployeeService
from ..services.data_service import DataService


router = APIRouter()
employee_service = EmployeeService()
data_service = DataService()


@router.get("/", response_model=List[Department])
async def get_departments():
    """Get all departments"""
    return list(data_service.departments.values())


@router.get("/{department_id}", response_model=Department)
async def get_department(department_id: str):
    """Get department by ID"""
    department = data_service.departments.get(department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.get("/{department_id}/employees")
async def get_department_employees(department_id: str):
    """Get all employees in a department"""
    department = data_service.departments.get(department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return employee_service.get_employees_by_department(department_id)
