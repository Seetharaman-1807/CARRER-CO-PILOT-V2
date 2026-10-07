from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume, ResumeVersion
from app.models.job import JobDescription, ATSAnalysis, SkillGapAnalysis, ReadinessSnapshot, TargetRole
from app.models.skill import CandidateSkill
from app.models.dsa import DSAAttempt
from app.models.interview import InterviewResponse
from app.schemas.analysis import (
    ATSScoreRequest,
    ATSAnalysisResponse,
    SkillGapResponse,
    ReadinessResponse,
)
from app.api.deps import get_current_user
from app.engines.ats_scorer import calculate_ats_score
from app.engines.skill_gap_engine import analyze_skill_gaps
from app.engines.career_readiness_engine import calculate_career_readiness

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("/ats", response_model=ATSAnalysisResponse)
def compute_ats(
    req: ATSScoreRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    version = db.query(ResumeVersion).join(Resume).filter(
        ResumeVersion.id == req.resume_version_id,
        Resume.user_id == current_user.id
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found.")

    jd = db.query(JobDescription).filter(
        JobDescription.id == req.job_description_id,
        JobDescription.user_id == current_user.id
    ).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found.")

    required_skills = jd.parsed_requirements.get("required_skills", [])
    
    score_result = calculate_ats_score(
        resume_parsed=version.parsed_content,
        resume_raw_text=version.raw_text,
        jd_text=jd.content,
        jd_required_skills=required_skills
    )

    ats_record = ATSAnalysis(
        user_id=current_user.id,
        resume_version_id=version.id,
        job_description_id=jd.id,
        overall_score=score_result["overall_score"],
        scoring_version=score_result["scoring_version"],
        component_scores=score_result["components"],
        feedback=score_result
    )
    db.add(ats_record)
    db.commit()
    db.refresh(ats_record)

    return ats_record


@router.post("/skill-gap", response_model=SkillGapResponse)
def compute_skill_gaps(
    job_description_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch candidate skills
    candidate_skills = db.query(CandidateSkill).filter(CandidateSkill.user_id == current_user.id).all()
    cand_skill_dicts = [
        {"canonical_name": s.canonical_name, "score": s.score, "confidence": s.confidence}
        for s in candidate_skills
    ]

    # Get latest resume raw text if available
    latest_version = db.query(ResumeVersion).join(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(ResumeVersion.id.desc()).first()
    raw_text = latest_version.raw_text if latest_version else ""

    # Fetch JD or use standard role requirements
    required_skills = ["Python", "FastAPI", "SQL", "Docker", "System Design", "Data Structures & Algorithms"]
    preferred_skills = ["PostgreSQL", "Redis", "CI/CD"]
    target_role_id = None

    if job_description_id:
        jd = db.query(JobDescription).filter(
            JobDescription.id == job_description_id,
            JobDescription.user_id == current_user.id
        ).first()
        if jd:
            target_role_id = jd.target_role_id
            required_skills = jd.parsed_requirements.get("required_skills", required_skills)
            preferred_skills = jd.parsed_requirements.get("preferred_skills", preferred_skills)

    gap_result = analyze_skill_gaps(
        candidate_skills=cand_skill_dicts,
        candidate_raw_text=raw_text,
        jd_required_skills=required_skills,
        jd_preferred_skills=preferred_skills
    )

    gap_record = SkillGapAnalysis(
        user_id=current_user.id,
        target_role_id=target_role_id,
        job_description_id=job_description_id,
        gaps=gap_result["gaps"],
        summary=gap_result["summary"]
    )
    db.add(gap_record)
    db.commit()
    db.refresh(gap_record)

    return gap_record


@router.post("/readiness", response_model=ReadinessResponse)
def compute_readiness(
    target_role_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Latest ATS score
    latest_ats = db.query(ATSAnalysis).filter(
        ATSAnalysis.user_id == current_user.id
    ).order_by(ATSAnalysis.id.desc()).first()
    ats_score = latest_ats.overall_score if latest_ats else None

    # 2. Candidate skills
    skills = db.query(CandidateSkill).filter(CandidateSkill.user_id == current_user.id).all()
    skill_dicts = [{"canonical_name": s.canonical_name, "score": s.score, "confidence": s.confidence} for s in skills]

    # 3. DSA attempts
    dsa_attempts = db.query(DSAAttempt).filter(DSAAttempt.user_id == current_user.id).all()
    dsa_dicts = [{"execution_result": a.execution_result, "hints_used": a.hints_used} for a in dsa_attempts]

    # 4. Interview responses
    interview_responses = db.query(InterviewResponse).join(User, User.id == current_user.id).all()
    interview_dicts = [{"evaluation": r.evaluation} for r in interview_responses]

    # 5. Projects count
    latest_version = db.query(ResumeVersion).join(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(ResumeVersion.id.desc()).first()
    projects_count = len(latest_version.parsed_content.get("projects", [])) if latest_version else 0

    # 6. JD match
    latest_gap = db.query(SkillGapAnalysis).filter(
        SkillGapAnalysis.user_id == current_user.id
    ).order_by(SkillGapAnalysis.id.desc()).first()
    if latest_gap and latest_gap.summary.get("total_requirements", 0) > 0:
        exact = latest_gap.summary.get("exact_matches", 0)
        related = latest_gap.summary.get("related_matches", 0)
        total = latest_gap.summary["total_requirements"]
        jd_match_ratio = (exact + (related * 0.65)) / total
    else:
        jd_match_ratio = None

    readiness = calculate_career_readiness(
        ats_score=ats_score,
        candidate_skills=skill_dicts,
        dsa_attempts=dsa_dicts,
        interview_responses=interview_dicts,
        resume_projects_count=projects_count,
        jd_match_ratio=jd_match_ratio
    )

    snapshot = ReadinessSnapshot(
        user_id=current_user.id,
        target_role_id=target_role_id,
        overall_score=readiness["overall_score"],
        component_scores=readiness["components"],
        confidence=readiness["confidence"]
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "id": snapshot.id,
        "user_id": current_user.id,
        "target_role_id": target_role_id,
        "overall_score": snapshot.overall_score,
        "confidence": snapshot.confidence,
        "components": snapshot.component_scores,
        "created_at": snapshot.created_at
    }
