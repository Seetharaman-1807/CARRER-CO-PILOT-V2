from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class InterviewStartRequest(BaseModel):
    target_role_id: Optional[int] = None
    type: str = "technical"  # technical, behavioral, role-specific, project-based
    difficulty: str = "Medium"


class InterviewResponseSubmit(BaseModel):
    question_id: str
    response: str


class InterviewQuestionItem(BaseModel):
    id: str
    question: str
    category: str
    focus_skill: str


class InterviewResponseItem(BaseModel):
    id: int
    session_id: int
    question_id: str
    question_text: str
    user_response: str
    evaluation: Dict[str, Any]
    skill_evidence: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionResponse(BaseModel):
    id: int
    user_id: int
    target_role_id: Optional[int] = None
    type: str
    difficulty: str
    status: str
    current_question_idx: int
    questions: List[Dict[str, Any]]
    final_evaluation: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None
    responses: List[InterviewResponseItem] = []

    model_config = ConfigDict(from_attributes=True)
