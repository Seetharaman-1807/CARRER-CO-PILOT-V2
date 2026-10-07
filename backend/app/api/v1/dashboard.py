from typing import Dict, Any, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, CandidateProfile
from app.models.resume import Resume, ResumeVersion
from app.models.job import TargetRole, JobDescription, ATSAnalysis, SkillGapAnalysis, ReadinessSnapshot
from app.models.skill import CandidateSkill
from app.models.dsa import DSAAttempt
from app.models.interview import InterviewSession
from app.models.roadmap import Roadmap, RoadmapTask
from app.schemas.dashboard import DashboardResponse, DailyTaskItem, ActivityItem
from app.api.deps import get_current_user
from app.engines.career_readiness_engine import calculate_career_readiness
from app.engines.roadmap_engine import generate_daily_plan

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Target Role
    target_role_record = db.query(TargetRole).filter(
        TargetRole.user_id == current_user.id,
        TargetRole.is_primary == True
    ).first()
    target_role_name = target_role_record.role_name if target_role_record else "Backend Developer"

    # 2. Latest Resume & ATS
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    latest_version = db.query(ResumeVersion).join(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(ResumeVersion.id.desc()).first()

    latest_ats = db.query(ATSAnalysis).filter(
        ATSAnalysis.user_id == current_user.id
    ).order_by(ATSAnalysis.id.desc()).first()
    ats_score = latest_ats.overall_score if latest_ats else None

    # 3. Candidate Skills
    candidate_skills = db.query(CandidateSkill).filter(CandidateSkill.user_id == current_user.id).all()
    cand_skill_dicts = [{"canonical_name": s.canonical_name, "score": s.score, "confidence": s.confidence} for s in candidate_skills]

    # 4. DSA attempts & Interview responses
    dsa_attempts = db.query(DSAAttempt).filter(DSAAttempt.user_id == current_user.id).all()
    dsa_dicts = [{"execution_result": a.execution_result, "hints_used": a.hints_used} for a in dsa_attempts]

    interview_sessions = db.query(InterviewSession).filter(InterviewSession.user_id == current_user.id).all()
    interview_responses = []
    for s in interview_sessions:
        for r in s.responses:
            interview_responses.append({"evaluation": r.evaluation})

    # 5. Skill Gaps
    latest_gap = db.query(SkillGapAnalysis).filter(
        SkillGapAnalysis.user_id == current_user.id
    ).order_by(SkillGapAnalysis.id.desc()).first()

    top_gaps = latest_gap.gaps if latest_gap else []
    jd_match_ratio = None
    if latest_gap and latest_gap.summary.get("total_requirements", 0) > 0:
        exact = latest_gap.summary.get("exact_matches", 0)
        related = latest_gap.summary.get("related_matches", 0)
        total = latest_gap.summary["total_requirements"]
        jd_match_ratio = (exact + (related * 0.65)) / total

    # 6. Career Readiness calculation
    readiness = calculate_career_readiness(
        ats_score=ats_score,
        candidate_skills=cand_skill_dicts,
        dsa_attempts=dsa_dicts,
        interview_responses=interview_responses,
        resume_projects_count=len(latest_version.parsed_content.get("projects", [])) if latest_version else 0,
        jd_match_ratio=jd_match_ratio
    )

    # 7. Next Best Action determination
    if not latest_version:
        next_action = {
            "title": "Upload Your Resume",
            "description": "Upload your resume (PDF/DOCX) to extract evidence-backed skills and compute your baseline ATS score.",
            "action_route": "/resumes",
            "button_text": "Upload Resume Now"
        }
    elif not top_gaps:
        next_action = {
            "title": "Analyze Target Job Description",
            "description": "Add a job description for your target role to identify concrete skill gaps and calculate alignment.",
            "action_route": "/jobs",
            "button_text": "Add Job Description"
        }
    elif not dsa_attempts:
        next_action = {
            "title": "Complete First DSA Challenge",
            "description": "Solve your first algorithmic challenge to benchmark problem-solving readiness.",
            "action_route": "/dsa",
            "button_text": "Solve Problem"
        }
    elif not interview_sessions:
        next_action = {
            "title": "Practice Mock Technical Interview",
            "description": "Simulate a live interview round to evaluate technical depth and verbal reasoning.",
            "action_route": "/interviews",
            "button_text": "Start Mock Interview"
        }
    else:
        top_gap_name = top_gaps[0].get("canonical_skill", "Technical Skills") if top_gaps else "Technical Skills"
        next_action = {
            "title": f"Focus On High-Impact Gap: {top_gap_name}",
            "description": f"Complete the roadmap milestone for {top_gap_name} to lift career readiness score.",
            "action_route": "/roadmap",
            "button_text": "View Roadmap Task"
        }

    # 8. Today's Plan
    daily_tasks_data = generate_daily_plan(tasks=[], top_gaps=top_gaps)
    todays_plan = [DailyTaskItem(**item) for item in daily_tasks_data]

    # 9. Recent Activity Timeline
    recent_activity: List[ActivityItem] = []
    if latest_version:
        recent_activity.append(ActivityItem(
            id=f"res_{latest_version.id}",
            type="resume",
            title=f"Uploaded Resume V{latest_version.version_number} ({latest_version.file_name})",
            timestamp=latest_version.created_at,
            score_or_status=f"Parsed {len(latest_version.parsed_content.get('skills', []))} skills"
        ))
    for a in dsa_attempts[-2:]:
        recent_activity.append(ActivityItem(
            id=f"dsa_{a.id}",
            type="dsa",
            title=f"DSA Submission on {a.problem.title}",
            timestamp=a.created_at,
            score_or_status="Passed" if a.execution_result.get("passed") else "Tests failed"
        ))
    for s in interview_sessions[-2:]:
        recent_activity.append(ActivityItem(
            id=f"int_{s.id}",
            type="interview",
            title=f"{s.type.capitalize()} Mock Interview Session",
            timestamp=s.created_at,
            score_or_status=s.status.capitalize()
        ))

    # Sort recent activity descending
    recent_activity.sort(key=lambda x: x.timestamp, reverse=True)

    # 10. Progress Trend Mock/Historical
    progress_trend = [
        {"milestone": "Day 1 (Initial)", "readiness": max(20.0, readiness["overall_score"] - 25.0)},
        {"milestone": "Day 3 (Resume Ingestion)", "readiness": max(35.0, readiness["overall_score"] - 12.0)},
        {"milestone": "Current Readiness", "readiness": readiness["overall_score"]},
    ]

    resume_status = {
        "has_resume": bool(latest_version),
        "version_number": latest_version.version_number if latest_version else 0,
        "file_name": latest_version.file_name if latest_version else "No resume uploaded",
        "ats_score": ats_score,
        "skills_extracted_count": len(latest_version.parsed_content.get("skills", [])) if latest_version else 0
    }

    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    upcoming_interview = None
    if profile and profile.target_interview_date:
        upcoming_interview = {
            "date": profile.target_interview_date.isoformat(),
            "target_role": target_role_name,
            "days_remaining": max(0, (profile.target_interview_date.date() - datetime.now(timezone.utc).date()).days)
        }

    return DashboardResponse(
        career_readiness=readiness["overall_score"],
        confidence=readiness["confidence"],
        target_role=target_role_name,
        next_best_action=next_action,
        readiness_breakdown=readiness["components"],
        top_skill_gaps=top_gaps[:3],
        todays_plan=todays_plan,
        progress_trend=progress_trend,
        recent_activity=recent_activity[:5],
        resume_status=resume_status,
        upcoming_interview=upcoming_interview
    )
