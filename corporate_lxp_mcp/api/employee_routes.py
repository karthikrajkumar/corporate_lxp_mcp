"""Employee API routes following SOLID principles"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..models.employee import Employee, EmployeeCreate, EmployeeUpdate
from ..services.employee_service import EmployeeService


router = APIRouter()
employee_service = EmployeeService()


@router.get("/", response_model=List[Employee])
async def get_employees(
    department: Optional[str] = Query(None, description="Filter by department ID"),
    role: Optional[str] = Query(None, description="Filter by role"),
    manager: Optional[str] = Query(None, description="Filter by manager ID"),
    search: Optional[str] = Query(None, description="Search by name or email")
):
    """Get all employees with optional filtering"""
    employees = employee_service.get_all_employees()
    
    if department:
        employees = [emp for emp in employees if emp.department_id == department]
    
    if role:
        employees = [emp for emp in employees if emp.role.value == role]
    
    if manager:
        employees = [emp for emp in employees if emp.manager_id == manager]
    
    if search:
        employees = employee_service.search_employees(search)
    
    return employees


@router.get("/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    """Get employee by ID"""
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.get("/email/{email}", response_model=Employee)
async def get_employee_by_email(email: str):
    """Get employee by email"""
    employee = employee_service.get_employee_by_email(email)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("/", response_model=Employee, status_code=201)
async def create_employee(employee_create: EmployeeCreate):
    """Create a new employee"""
    try:
        return employee_service.create_employee(employee_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{employee_id}", response_model=Employee)
async def update_employee(employee_id: str, employee_update: EmployeeUpdate):
    """Update employee information"""
    employee = employee_service.update_employee(employee_id, employee_update)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.delete("/{employee_id}", status_code=204)
async def delete_employee(employee_id: str):
    """Delete an employee"""
    try:
        success = employee_service.delete_employee(employee_id)
        if not success:
            raise HTTPException(status_code=404, detail="Employee not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{employee_id}/training")
async def get_employee_training(employee_id: str):
    """Get employee training assignments"""
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return employee_service.get_employee_training_assignments(employee_id)


@router.get("/{employee_id}/skills")
async def get_employee_skills(employee_id: str):
    """Get employee skill assessments"""
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return employee_service.get_employee_skill_assessments(employee_id)


@router.get("/department/{department_id}", response_model=List[Employee])
async def get_employees_by_department(department_id: str):
    """Get all employees in a department"""
    return employee_service.get_employees_by_department(department_id)


@router.get("/manager/{manager_id}", response_model=List[Employee])
async def get_employees_by_manager(manager_id: str):
    """Get all employees reporting to a manager"""
    return employee_service.get_employees_by_manager(manager_id)
