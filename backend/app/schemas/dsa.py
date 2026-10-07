from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DSAProblemSummary(BaseModel):
    id: int
    title: str
    slug: str
    topic: str
    difficulty: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class DSAProblemDetail(BaseModel):
    id: int
    title: str
    slug: str
    topic: str
    difficulty: str
    description: str
    starter_code: str
    test_cases: List[Dict[str, Any]]
    hints: List[str]

    model_config = ConfigDict(from_attributes=True)


class DSAAttemptCreate(BaseModel):
    problem_id: int
    code: str
    hints_used: Optional[int] = 0


class DSAAttemptResponse(BaseModel):
    id: int
    user_id: int
    problem_id: int
    code: str
    attempt_count: int
    hints_used: int
    execution_result: Dict[str, Any]
    complexity_score: Optional[float] = None
    skill_evidence: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
