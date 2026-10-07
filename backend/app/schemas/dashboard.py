from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.schemas.analysis import ReadinessComponent, SkillGapItem
from app.schemas.roadmap import RoadmapTaskResponse


class DailyTaskItem(BaseModel):
    task: str
    reason: str
    skill: str
    estimated_time: str
    priority: str
    completion_criteria: str


class ActivityItem(BaseModel):
    id: str
    type: str  # resume, dsa, interview, roadmap
    title: str
    timestamp: datetime
    score_or_status: str


class DashboardResponse(BaseModel):
    career_readiness: float
    confidence: str
    target_role: Optional[str] = "Software Engineer"
    next_best_action: Dict[str, str]
    readiness_breakdown: Dict[str, ReadinessComponent]
    top_skill_gaps: List[SkillGapItem]
    todays_plan: List[DailyTaskItem]
    progress_trend: List[Dict[str, Any]]
    recent_activity: List[ActivityItem]
    resume_status: Dict[str, Any]
    upcoming_interview: Optional[Dict[str, Any]] = None
