"""Data models for Corporate LXP platform"""

from .employee import Employee, EmployeeCreate, EmployeeUpdate
from .department import Department
from .training import TrainingProgram, TrainingAssignment
from .skills import SkillAssessment, Skill

__all__ = [
    "Employee",
    "EmployeeCreate", 
    "EmployeeUpdate",
    "Department",
    "TrainingProgram",
    "TrainingAssignment",
    "SkillAssessment",
    "Skill"
]
