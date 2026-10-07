from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ATSComponentScores(BaseModel):
    keyword_match: float
    technical_skill_match: float
    experience_match: float
    education_match: float
    project_relevance: float
    formatting: float
    section_completeness: float


class ATSScoreRequest(BaseModel):
    resume_version_id: int
    job_description_id: int


class ATSAnalysisResponse(BaseModel):
    id: int
    user_id: int
    resume_version_id: int
    job_description_id: int
    overall_score: float
    scoring_version: str
    component_scores: Dict[str, float]
    feedback: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillGapItem(BaseModel):
    skill: str
    canonical_skill: str
    status: str  # exact, related, partial, missing
    importance: float
    candidate_score: float
    reason: str
    priority: str  # High, Medium, Low


class SkillGapResponse(BaseModel):
    id: int
    user_id: int
    target_role_id: Optional[int] = None
    job_description_id: Optional[int] = None
    gaps: List[SkillGapItem]
    summary: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReadinessComponent(BaseModel):
    name: str
    score: float
    confidence: str
    evidence: str
    last_updated: Optional[datetime] = None


class ReadinessResponse(BaseModel):
    id: Optional[int] = None
    user_id: int
    target_role_id: Optional[int] = None
    overall_score: float
    confidence: str
    components: Dict[str, ReadinessComponent]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
