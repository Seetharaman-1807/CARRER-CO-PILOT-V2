from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ResumeEvidenceItem(BaseModel):
    id: Optional[int] = None
    entity_type: str
    entity_value: str
    evidence_text: str
    section: str
    confidence: float

    model_config = ConfigDict(from_attributes=True)


class ResumeVersionResponse(BaseModel):
    id: int
    resume_id: int
    version_number: int
    file_name: str
    parsed_content: Dict[str, Any]
    raw_text: Optional[str] = ""
    created_at: datetime
    evidence: Optional[List[ResumeEvidenceItem]] = []

    model_config = ConfigDict(from_attributes=True)


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    title: str
    current_version_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    versions: List[ResumeVersionResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ResumeCompareResponse(BaseModel):
    v1_id: int
    v2_id: int
    v1_version: int
    v2_version: int
    ats_score_delta: float
    skills_added: List[str]
    skills_removed: List[str]
    new_projects: List[str]
    improvements: List[str]
