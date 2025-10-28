"""Employee service following SOLID principles"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from ..models.employee import Employee, EmployeeCreate, EmployeeUpdate, EmployeeStatus
from ..models.department import Department
from ..models.training import TrainingAssignment
from ..models.skills import SkillAssessment
from .data_service import DataService


class EmployeeService:
    """Service class handling employee business logic"""

    def __init__(self):
        """Initialize service with data access"""
        self._data_service = DataService()

    def get_all_employees(self) -> List[Employee]:
        """Retrieve all employees"""
        return list(self._data_service.employees.values())

    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Retrieve employee by ID"""
        return self._data_service.employees.get(employee_id)

    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Retrieve employee by email"""
        for employee in self._data_service.employees.values():
            if employee.email == email:
                return employee
        return None

    def create_employee(self, employee_create: EmployeeCreate) -> Employee:
        """Create a new employee"""
        # Validate email uniqueness
        if self.get_employee_by_email(employee_create.email):
            raise ValueError(f"Employee with email {employee_create.email} already exists")

        # Validate department exists
        if employee_create.department_id not in self._data_service.departments:
            raise ValueError(f"Department {employee_create.department_id} does not exist")

        # Validate manager exists if specified
        if employee_create.manager_id:
            if employee_create.manager_id not in self._data_service.employees:
                raise ValueError(f"Manager {employee_create.manager_id} does not exist")

        employee = Employee(
            id=str(uuid4()),
            email=employee_create.email,
            first_name=employee_create.first_name,
            last_name=employee_create.last_name,
            department_id=employee_create.department_id,
            role=employee_create.role,
            manager_id=employee_create.manager_id,
            hire_date=datetime.now(),
            location=employee_create.location,
            phone=employee_create.phone,
            status=EmployeeStatus.ACTIVE
        )

        self._data_service.employees[employee.id] = employee
        return employee

    def update_employee(self, employee_id: str, employee_update: EmployeeUpdate) -> Optional[Employee]:
        """Update employee information"""
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            return None

        # Validate department exists if being updated
        if employee_update.department_id:
            if employee_update.department_id not in self._data_service.departments:
                raise ValueError(f"Department {employee_update.department_id} does not exist")

        # Validate manager exists if being updated
        if employee_update.manager_id:
            if employee_update.manager_id not in self._data_service.employees:
                raise ValueError(f"Manager {employee_update.manager_id} does not exist")

        # Update fields
        update_data = employee_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)

        employee.updated_at = datetime.now()
        return employee

    def delete_employee(self, employee_id: str) -> bool:
        """Delete an employee"""
        if employee_id not in self._data_service.employees:
            return False

        # Check if employee is a manager
        employees_managed = self.get_employees_by_manager(employee_id)
        if employees_managed:
            raise ValueError(f"Cannot delete employee {employee_id} as they manage other employees")

        del self._data_service.employees[employee_id]
        return True

    def get_employees_by_department(self, department_id: str) -> List[Employee]:
        """Get all employees in a department"""
        return [
            emp for emp in self._data_service.employees.values()
            if emp.department_id == department_id
        ]

    def get_employees_by_manager(self, manager_id: str) -> List[Employee]:
        """Get all employees reporting to a manager"""
        return [
            emp for emp in self._data_service.employees.values()
            if emp.manager_id == manager_id
        ]

    def get_employees_by_role(self, role: str) -> List[Employee]:
        """Get all employees with a specific role"""
        return [
            emp for emp in self._data_service.employees.values()
            if emp.role.value == role
        ]

    def get_employee_training_assignments(self, employee_id: str) -> List[TrainingAssignment]:
        """Get all training assignments for an employee"""
        return [
            assignment for assignment in self._data_service.training_assignments.values()
            if assignment.employee_id == employee_id
        ]

    def get_employee_skill_assessments(self, employee_id: str) -> List[SkillAssessment]:
        """Get all skill assessments for an employee"""
        return [
            assessment for assessment in self._data_service.skill_assessments.values()
            if assessment.employee_id == employee_id
        ]

    def search_employees(self, query: str) -> List[Employee]:
        """Search employees by name or email"""
        query = query.lower()
        return [
            emp for emp in self._data_service.employees.values()
            if query in emp.first_name.lower() or 
               query in emp.last_name.lower() or 
               query in emp.email.lower()
        ]
