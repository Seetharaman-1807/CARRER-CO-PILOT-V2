from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SkillEvidenceResponse(BaseModel):
    id: int
    candidate_skill_id: int
    source_type: str
    source_id: Optional[str] = None
    score: float
    confidence: float
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateSkillResponse(BaseModel):
    id: int
    user_id: int
    skill_id: Optional[int] = None
    canonical_name: str
    score: float
    confidence: str
    target_score: float
    trend: str
    updated_at: datetime
    evidence_items: Optional[List[SkillEvidenceResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class CandidateSkillUpdate(BaseModel):
    score: Optional[float] = None
    target_score: Optional[float] = None


class SkillTaxonomyItem(BaseModel):
    id: int
    canonical_name: str
    category: str
    parent_skill_id: Optional[int] = None
    aliases: List[str] = []

    model_config = ConfigDict(from_attributes=True)
