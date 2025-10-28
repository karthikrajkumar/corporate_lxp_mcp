"""Skills and assessment models following SOLID principles"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SkillLevel(str, Enum):
    """Skill proficiency levels"""
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillCategory(str, Enum):
    """Skill categories for corporate environment"""
    TECHNICAL = "technical"
    LEADERSHIP = "leadership"
    COMMUNICATION = "communication"
    PROJECT_MANAGEMENT = "project_management"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    BUSINESS = "business"


class Skill(BaseModel):
    """Skill entity model"""
    id: str = Field(..., description="Unique skill identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Skill name")
    description: str = Field(..., description="Skill description")
    category: SkillCategory = Field(..., description="Skill category")
    relevant_roles: List[str] = Field(default_factory=list, description="Roles where this skill is relevant")
    created_at: datetime = Field(default_factory=datetime.now, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SkillAssessment(BaseModel):
    """Skill assessment model for employees"""
    id: str = Field(..., description="Unique assessment identifier")
    employee_id: str = Field(..., description="Employee identifier")
    skill_id: str = Field(..., description="Skill identifier")
    current_level: SkillLevel = Field(..., description="Current skill level")
    target_level: SkillLevel = Field(..., description="Target skill level")
    assessed_by: str = Field(..., description="Employee ID who conducted assessment")
    assessment_date: datetime = Field(default_factory=datetime.now, description="Assessment timestamp")
    notes: Optional[str] = Field(None, description="Assessment notes")
    gap_analysis: Optional[str] = Field(None, description="Skill gap analysis")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
