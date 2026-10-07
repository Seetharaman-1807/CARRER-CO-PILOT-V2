from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, CandidateProfile
from app.schemas.profile import ProfileUpdate, ProfileResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("", response_model=ProfileResponse)
def update_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)

    if profile_in.education is not None:
        profile.education = profile_in.education
    if profile_in.experience_summary is not None:
        profile.experience_summary = profile_in.experience_summary
    if profile_in.career_goal is not None:
        profile.career_goal = profile_in.career_goal
    if profile_in.available_hours is not None:
        profile.available_hours = profile_in.available_hours
    if profile_in.target_interview_date is not None:
        profile.target_interview_date = profile_in.target_interview_date

    db.commit()
    db.refresh(profile)
    return profile
