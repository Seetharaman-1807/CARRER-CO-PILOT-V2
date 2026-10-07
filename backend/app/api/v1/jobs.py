from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.job import TargetRole, JobDescription, RoleRequirement
from app.schemas.job import (
    TargetRoleCreate,
    TargetRoleResponse,
    JobDescriptionCreate,
    JobDescriptionResponse,
)
from app.api.deps import get_current_user
from app.engines.jd_matcher import parse_job_description
from app.engines.skill_taxonomy import normalize_skill

router = APIRouter(tags=["jobs"])


@router.post("/target-roles", response_model=TargetRoleResponse)
def create_target_role(
    role_in: TargetRoleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # If primary, reset other roles
    if role_in.is_primary:
        db.query(TargetRole).filter(TargetRole.user_id == current_user.id).update({"is_primary": False})

    target_role = TargetRole(
        user_id=current_user.id,
        role_name=role_in.role_name,
        is_primary=role_in.is_primary if role_in.is_primary is not None else True
    )
    db.add(target_role)
    db.commit()
    db.refresh(target_role)
    return target_role


@router.get("/target-roles", response_model=List[TargetRoleResponse])
def get_target_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(TargetRole).filter(TargetRole.user_id == current_user.id).all()


@router.post("/job-descriptions", response_model=JobDescriptionResponse)
def create_job_description(
    jd_in: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    parsed = parse_job_description(jd_in.content)

    jd = JobDescription(
        user_id=current_user.id,
        target_role_id=jd_in.target_role_id,
        title=jd_in.title or parsed["title"],
        company=jd_in.company,
        content=jd_in.content,
        parsed_requirements=parsed
    )
    db.add(jd)
    db.flush()

    # Store individual role requirements
    for skill in parsed.get("required_skills", []):
        req = RoleRequirement(
            job_description_id=jd.id,
            skill_name=skill,
            canonical_skill=normalize_skill(skill),
            requirement_type="required",
            importance=1.0,
            evidence=f"Extracted as core required skill from JD: '{skill}'"
        )
        db.add(req)

    for skill in parsed.get("preferred_skills", []):
        req = RoleRequirement(
            job_description_id=jd.id,
            skill_name=skill,
            canonical_skill=normalize_skill(skill),
            requirement_type="preferred",
            importance=0.6,
            evidence=f"Extracted as preferred qualification: '{skill}'"
        )
        db.add(req)

    db.commit()
    db.refresh(jd)
    return jd


@router.get("/job-descriptions", response_model=List[JobDescriptionResponse])
def get_job_descriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(JobDescription).filter(JobDescription.user_id == current_user.id).order_by(JobDescription.created_at.desc()).all()
