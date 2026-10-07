from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TargetRoleCreate(BaseModel):
    role_name: str
    is_primary: Optional[bool] = True


class TargetRoleResponse(BaseModel):
    id: int
    user_id: int
    role_name: str
    is_primary: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobDescriptionCreate(BaseModel):
    title: str
    company: Optional[str] = None
    content: str
    target_role_id: Optional[int] = None


class RoleRequirementItem(BaseModel):
    id: int
    skill_name: str
    canonical_skill: str
    requirement_type: str
    importance: float
    evidence: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class JobDescriptionResponse(BaseModel):
    id: int
    user_id: int
    target_role_id: Optional[int] = None
    title: str
    company: Optional[str] = None
    content: str
    parsed_requirements: Dict[str, Any] = {}
    created_at: datetime
    requirements: Optional[List[RoleRequirementItem]] = []

    model_config = ConfigDict(from_attributes=True)
