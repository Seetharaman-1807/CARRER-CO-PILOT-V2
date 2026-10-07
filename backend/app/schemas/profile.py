from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProfileUpdate(BaseModel):
    education: Optional[str] = None
    experience_summary: Optional[str] = None
    career_goal: Optional[str] = None
    available_hours: Optional[int] = 10
    target_interview_date: Optional[datetime] = None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    education: Optional[str] = None
    experience_summary: Optional[str] = None
    career_goal: Optional[str] = None
    available_hours: int = 10
    target_interview_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
