"""Service layer for Corporate LXP platform"""

from .employee_service import EmployeeService
from .data_service import DataService

__all__ = ["EmployeeService", "DataService"]
