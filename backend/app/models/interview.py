from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role_id = Column(Integer, ForeignKey("target_roles.id", ondelete="SET NULL"), nullable=True)
    type = Column(String(50), nullable=False, default="technical")  # technical, behavioral, role-specific, project-based
    difficulty = Column(String(50), nullable=False, default="Medium")
    status = Column(String(50), nullable=False, default="in_progress")  # in_progress, completed
    current_question_idx = Column(Integer, nullable=False, default=0)
    questions = Column(JSON, nullable=False, default=list)
    final_evaluation = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="interview_sessions")
    responses = relationship("InterviewResponse", back_populates="session", cascade="all, delete-orphan", order_by="InterviewResponse.id")


class InterviewResponse(Base):
    __tablename__ = "interview_responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(100), nullable=False)
    question_text = Column(Text, nullable=False)
    user_response = Column(Text, nullable=False)
    evaluation = Column(JSON, nullable=False, default=dict)  # technical_accuracy, clarity, depth, feedback, score
    skill_evidence = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    session = relationship("InterviewSession", back_populates="responses")
