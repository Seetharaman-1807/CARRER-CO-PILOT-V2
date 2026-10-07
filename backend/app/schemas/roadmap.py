from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RoadmapTaskResponse(BaseModel):
    id: int
    roadmap_id: int
    skill_name: str
    title: str
    description: str
    priority: str
    estimated_minutes: int
    status: str
    due_date: Optional[datetime] = None
    completion_criteria: Optional[str] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RoadmapTaskUpdate(BaseModel):
    status: str  # pending, completed


class RoadmapResponse(BaseModel):
    id: int
    user_id: int
    target_role_id: Optional[int] = None
    title: str
    status: str
    goal: Optional[str] = None
    weekly_plan: List[Dict[str, Any]] = []
    tasks: List[RoadmapTaskResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoadmapGenerateRequest(BaseModel):
    target_role_id: Optional[int] = None
    focus_skills: Optional[List[str]] = None
