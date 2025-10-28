"""Training program models following SOLID principles"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TrainingStatus(str, Enum):
    """Training program status"""
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class TrainingType(str, Enum):
    """Types of corporate training"""
    ONBOARDING = "onboarding"
    COMPLIANCE = "compliance"
    TECHNICAL = "technical"
    LEADERSHIP = "leadership"
    SOFT_SKILLS = "soft_skills"
    SAFETY = "safety"


class TrainingProgram(BaseModel):
    """Training program entity model"""
    id: str = Field(..., description="Unique training program identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Training program title")
    description: str = Field(..., description="Training program description")
    training_type: TrainingType = Field(..., description="Type of training")
    duration_hours: int = Field(..., gt=0, description="Duration in hours")
    required_for_roles: List[str] = Field(default_factory=list, description="Roles that require this training")
    department_ids: List[str] = Field(default_factory=list, description="Departments this training applies to")
    is_mandatory: bool = Field(default=False, description="Whether training is mandatory")
    expiry_months: Optional[int] = Field(None, description="Training validity in months")
    created_at: datetime = Field(default_factory=datetime.now, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TrainingAssignment(BaseModel):
    """Training assignment model linking employees to training programs"""
    id: str = Field(..., description="Unique assignment identifier")
    employee_id: str = Field(..., description="Employee identifier")
    training_program_id: str = Field(..., description="Training program identifier")
    assigned_by: str = Field(..., description="Employee ID who assigned this training")
    assigned_at: datetime = Field(default_factory=datetime.now, description="Assignment timestamp")
    due_date: Optional[datetime] = Field(None, description="Training due date")
    status: TrainingStatus = Field(default=TrainingStatus.ASSIGNED, description="Training status")
    completion_date: Optional[datetime] = Field(None, description="Training completion date")
    score: Optional[int] = Field(None, ge=0, le=100, description="Training completion score")
    certificate_url: Optional[str] = Field(None, description="Certificate URL if completed")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
