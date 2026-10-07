from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.dsa import DSAProblem, DSAAttempt
from app.schemas.dsa import (
    DSAProblemSummary,
    DSAProblemDetail,
    DSAAttemptCreate,
    DSAAttemptResponse
)
from app.api.deps import get_current_user
from app.engines.dsa_engine import CURATED_DSA_PROBLEMS, execute_dsa_solution
from app.engines.adaptive_update_engine import record_skill_performance

router = APIRouter(prefix="/dsa", tags=["dsa"])


def seed_problems_if_needed(db: Session):
    count = db.query(DSAProblem).count()
    if count == 0:
        for p in CURATED_DSA_PROBLEMS:
            problem = DSAProblem(
                title=p["title"],
                slug=p["slug"],
                topic=p["topic"],
                difficulty=p["difficulty"],
                description=p["description"],
                starter_code=p["starter_code"],
                test_cases=p["test_cases"],
                hints=p["hints"]
            )
            db.add(problem)
        db.commit()


@router.get("/problems", response_model=List[DSAProblemSummary])
def get_problems(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    seed_problems_if_needed(db)
    return db.query(DSAProblem).all()


@router.get("/problems/{slug}", response_model=DSAProblemDetail)
def get_problem_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    seed_problems_if_needed(db)
    problem = db.query(DSAProblem).filter(DSAProblem.slug == slug).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")
    return problem


@router.post("/attempts", response_model=DSAAttemptResponse)
def submit_dsa_attempt(
    attempt_in: DSAAttemptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    seed_problems_if_needed(db)
    problem = db.query(DSAProblem).filter(DSAProblem.id == attempt_in.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")

    # Execute solution through safe AST execution harness
    exec_result = execute_dsa_solution(
        code_str=attempt_in.code,
        test_cases=problem.test_cases
    )

    is_passed = exec_result.get("passed", False)
    performance_score = 90.0 if is_passed else (40.0 if exec_result.get("passed_count", 0) > 0 else 20.0)
    
    # Adjust for hints used
    performance_score = max(10.0, performance_score - (attempt_in.hints_used * 5.0))

    previous_attempts_count = db.query(DSAAttempt).filter(
        DSAAttempt.user_id == current_user.id,
        DSAAttempt.problem_id == problem.id
    ).count()

    attempt = DSAAttempt(
        user_id=current_user.id,
        problem_id=problem.id,
        code=attempt_in.code,
        attempt_count=previous_attempts_count + 1,
        hints_used=attempt_in.hints_used or 0,
        execution_result=exec_result,
        complexity_score=8.0 if is_passed else 4.0,
        skill_evidence={
            "topic": problem.topic,
            "passed": is_passed,
            "runtime_ms": exec_result.get("runtime_ms", 0.0)
        }
    )
    db.add(attempt)
    db.flush()

    # Feed results into Candidate Skill Profile!
    record_skill_performance(
        db=db,
        user_id=current_user.id,
        skill_name=problem.topic,
        performance_score=performance_score,
        source_type="dsa",
        source_id=f"dsa_p{problem.id}_a{attempt.id}",
        evidence_weight=0.35,
        notes=f"DSA '{problem.title}' ({problem.topic}) attempt: {'Passed' if is_passed else 'Failed tests'}"
    )

    db.commit()
    db.refresh(attempt)
    return attempt
