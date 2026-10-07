from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.job import TargetRole
from app.models.interview import InterviewSession, InterviewResponse
from app.schemas.interview import (
    InterviewStartRequest,
    InterviewResponseSubmit,
    InterviewSessionResponse,
    InterviewResponseItem
)
from app.api.deps import get_current_user
from app.engines.interview_engine import (
    get_interview_questions_for_role,
    evaluate_interview_response,
)
from app.engines.adaptive_update_engine import record_skill_performance

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("", response_model=InterviewSessionResponse)
def start_interview(
    req: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_role = None
    if req.target_role_id:
        target_role = db.query(TargetRole).filter(
            TargetRole.id == req.target_role_id,
            TargetRole.user_id == current_user.id
        ).first()
    if not target_role:
        target_role = db.query(TargetRole).filter(
            TargetRole.user_id == current_user.id,
            TargetRole.is_primary == True
        ).first()

    role_name = target_role.role_name if target_role else "Backend Developer"
    questions = get_interview_questions_for_role(role_name, req.type)

    session = InterviewSession(
        user_id=current_user.id,
        target_role_id=target_role.id if target_role else None,
        type=req.type,
        difficulty=req.difficulty,
        status="in_progress",
        current_question_idx=0,
        questions=questions,
        final_evaluation={}
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{id}", response_model=InterviewSessionResponse)
def get_interview_session(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(
        InterviewSession.id == id,
        InterviewSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return session


@router.post("/{id}/responses", response_model=InterviewResponseItem)
def submit_interview_response(
    id: int,
    sub_in: InterviewResponseSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(
        InterviewSession.id == id,
        InterviewSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    # Locate question
    question_data = next((q for q in session.questions if q["id"] == sub_in.question_id), None)
    if not question_data:
        raise HTTPException(status_code=400, detail="Invalid question ID for this session.")

    # Evaluate response with rubric
    evaluation = evaluate_interview_response(question_data, sub_in.response)

    resp_record = InterviewResponse(
        session_id=session.id,
        question_id=sub_in.question_id,
        question_text=question_data["question"],
        user_response=sub_in.response,
        evaluation=evaluation,
        skill_evidence=evaluation.get("skill_evidence", {})
    )
    db.add(resp_record)
    db.flush()

    # Advance current question pointer
    if session.current_question_idx < len(session.questions) - 1:
        session.current_question_idx += 1

    # Feed skill evidence into Candidate Skill Profile!
    focus_skill = question_data.get("focus_skill", "General")
    record_skill_performance(
        db=db,
        user_id=current_user.id,
        skill_name=focus_skill,
        performance_score=float(evaluation["overall"]) * 10.0,
        source_type="interview",
        source_id=f"interview_s{session.id}_q{sub_in.question_id}",
        evidence_weight=0.3,
        notes=f"Interview question '{question_data['question'][:60]}' scored {evaluation['overall']}/10"
    )

    db.commit()
    db.refresh(resp_record)
    return resp_record


@router.post("/{id}/complete", response_model=InterviewSessionResponse)
def complete_interview(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(
        InterviewSession.id == id,
        InterviewSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    responses = session.responses
    if responses:
        avg_acc = sum([r.evaluation.get("technical_accuracy", 5.0) for r in responses]) / len(responses)
        avg_depth = sum([r.evaluation.get("depth", 5.0) for r in responses]) / len(responses)
        avg_clarity = sum([r.evaluation.get("clarity", 5.0) for r in responses]) / len(responses)
        avg_overall = sum([r.evaluation.get("overall", 5.0) for r in responses]) / len(responses)

        all_strengths = []
        all_improvements = []
        for r in responses:
            all_strengths.extend(r.evaluation.get("strengths", []))
            all_improvements.extend(r.evaluation.get("improvements", []))

        final_eval = {
            "technical_accuracy": round(avg_acc, 1),
            "depth": round(avg_depth, 1),
            "clarity": round(avg_clarity, 1),
            "overall": round(avg_overall, 1),
            "strengths": list(set(all_strengths))[:4],
            "improvements": list(set(all_improvements))[:4],
            "summary": f"Completed {len(responses)} questions with an overall interview score of {avg_overall:.1f}/10."
        }
    else:
        final_eval = {"overall": 0.0, "summary": "No answers submitted."}

    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc)
    session.final_evaluation = final_eval

    db.commit()
    db.refresh(session)
    return session
