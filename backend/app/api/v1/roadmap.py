from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, CandidateProfile
from app.models.job import TargetRole, SkillGapAnalysis
from app.models.skill import CandidateSkill
from app.models.roadmap import Roadmap, RoadmapTask
from app.schemas.roadmap import (
    RoadmapResponse,
    RoadmapGenerateRequest,
    RoadmapTaskUpdate,
    RoadmapTaskResponse
)
from app.api.deps import get_current_user
from app.engines.roadmap_engine import generate_adaptive_roadmap
from app.engines.adaptive_update_engine import record_skill_performance

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.get("", response_model=Optional[RoadmapResponse])
def get_current_roadmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    roadmap = db.query(Roadmap).filter(
        Roadmap.user_id == current_user.id,
        Roadmap.status == "active"
    ).order_by(Roadmap.id.desc()).first()
    return roadmap


@router.post("/generate", response_model=RoadmapResponse)
def create_roadmap(
    req: RoadmapGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    avail_hours = profile.available_hours if profile else 10

    target_role = db.query(TargetRole).filter(
        TargetRole.user_id == current_user.id,
        TargetRole.is_primary == True
    ).first()
    role_name = target_role.role_name if target_role else "Backend Developer"

    # Fetch top gaps
    gap_record = db.query(SkillGapAnalysis).filter(
        SkillGapAnalysis.user_id == current_user.id
    ).order_by(SkillGapAnalysis.id.desc()).first()
    top_gaps = gap_record.gaps if gap_record else []

    cand_skills = db.query(CandidateSkill).filter(CandidateSkill.user_id == current_user.id).all()
    cand_skill_dicts = [{"canonical_name": s.canonical_name, "score": s.score} for s in cand_skills]

    generated = generate_adaptive_roadmap(
        role_name=role_name,
        top_gaps=top_gaps,
        candidate_skills=cand_skill_dicts,
        available_hours=avail_hours
    )

    # Archive existing active roadmaps
    db.query(Roadmap).filter(
        Roadmap.user_id == current_user.id,
        Roadmap.status == "active"
    ).update({"status": "archived"})

    roadmap = Roadmap(
        user_id=current_user.id,
        target_role_id=target_role.id if target_role else None,
        title=generated["title"],
        status="active",
        goal=generated["goal"],
        weekly_plan=generated["weekly_plan"]
    )
    db.add(roadmap)
    db.flush()

    for t in generated["tasks"]:
        task_record = RoadmapTask(
            roadmap_id=roadmap.id,
            skill_name=t["skill_name"],
            title=t["title"],
            description=t["description"],
            priority=t["priority"],
            estimated_minutes=t["estimated_minutes"],
            status="pending",
            completion_criteria=t["completion_criteria"]
        )
        db.add(task_record)

    db.commit()
    db.refresh(roadmap)
    return roadmap


@router.post("/tasks/{id}/complete", response_model=RoadmapTaskResponse)
def complete_task(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(RoadmapTask).join(Roadmap).filter(
        RoadmapTask.id == id,
        Roadmap.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Roadmap task not found.")

    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)

    # When a roadmap task is completed, reward candidate skill profile!
    record_skill_performance(
        db=db,
        user_id=current_user.id,
        skill_name=task.skill_name,
        performance_score=85.0,
        source_type="roadmap",
        source_id=f"task_{task.id}",
        evidence_weight=0.3,
        notes=f"Successfully completed roadmap milestone: '{task.title}'"
    )

    db.commit()
    db.refresh(task)
    return task
