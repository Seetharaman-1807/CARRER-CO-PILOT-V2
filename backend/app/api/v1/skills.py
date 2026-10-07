from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.skill import CandidateSkill, SkillEvidence
from app.schemas.skill import CandidateSkillResponse, CandidateSkillUpdate
from app.api.deps import get_current_user
from app.engines.skill_taxonomy import CANONICAL_TAXONOMY, normalize_skill

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/taxonomy")
def get_skill_taxonomy():
    """Returns global canonical skills taxonomy and category tree."""
    return CANONICAL_TAXONOMY


@router.get("/profile", response_model=List[CandidateSkillResponse])
def get_candidate_skill_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    skills = db.query(CandidateSkill).filter(
        CandidateSkill.user_id == current_user.id
    ).order_by(CandidateSkill.score.desc()).all()
    return skills


@router.put("/profile/{id}", response_model=CandidateSkillResponse)
def update_candidate_skill(
    id: int,
    skill_in: CandidateSkillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    skill = db.query(CandidateSkill).filter(
        CandidateSkill.id == id,
        CandidateSkill.user_id == current_user.id
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill record not found.")

    if skill_in.score is not None:
        skill.score = min(100.0, max(0.0, skill_in.score))
    if skill_in.target_score is not None:
        skill.target_score = min(100.0, max(0.0, skill_in.target_score))

    db.commit()
    db.refresh(skill)
    return skill
