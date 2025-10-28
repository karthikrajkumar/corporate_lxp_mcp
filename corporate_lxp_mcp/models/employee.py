"""Employee model following SOLID principles"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class EmployeeRole(str, Enum):
    """Corporate employee roles"""
    EXECUTIVE = "executive"
    MANAGER = "manager"
    TEAM_LEAD = "team_lead"
    INDIVIDUAL_CONTRIBUTOR = "individual_contributor"
    HR = "hr"
    FINANCE = "finance"


class EmployeeStatus(str, Enum):
    """Employee employment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"


class Employee(BaseModel):
    """Employee entity model"""
    id: str = Field(..., description="Unique employee identifier")
    email: EmailStr = Field(..., description="Employee email address")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    department_id: str = Field(..., description="Department identifier")
    role: EmployeeRole = Field(..., description="Employee role")
    manager_id: Optional[str] = Field(None, description="Manager employee ID")
    status: EmployeeStatus = Field(default=EmployeeStatus.ACTIVE, description="Employment status")
    hire_date: datetime = Field(..., description="Date of hire")
    location: str = Field(..., description="Office location")
    phone: Optional[str] = Field(None, description="Phone number")
    created_at: datetime = Field(default_factory=datetime.now, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmployeeCreate(BaseModel):
    """DTO for creating new employees"""
    email: EmailStr = Field(..., description="Employee email address")
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    department_id: str = Field(..., description="Department identifier")
    role: EmployeeRole = Field(..., description="Employee role")
    manager_id: Optional[str] = Field(None, description="Manager employee ID")
    location: str = Field(..., description="Office location")
    phone: Optional[str] = Field(None, description="Phone number")


class EmployeeUpdate(BaseModel):
    """DTO for updating employee information"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Last name")
    department_id: Optional[str] = Field(None, description="Department identifier")
    role: Optional[EmployeeRole] = Field(None, description="Employee role")
    manager_id: Optional[str] = Field(None, description="Manager employee ID")
    status: Optional[EmployeeStatus] = Field(None, description="Employment status")
    location: Optional[str] = Field(None, description="Office location")
    phone: Optional[str] = Field(None, description="Phone number")
