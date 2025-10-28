"""Department model following SOLID principles"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Department(BaseModel):
    """Department entity model"""
    id: str = Field(..., description="Unique department identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Department name")
    description: Optional[str] = Field(None, description="Department description")
    head_id: Optional[str] = Field(None, description="Department head employee ID")
    parent_id: Optional[str] = Field(None, description="Parent department ID for sub-departments")
    location: str = Field(..., description="Primary office location")
    budget_code: Optional[str] = Field(None, description="Budget code for finance tracking")
    created_at: datetime = Field(default_factory=datetime.now, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
