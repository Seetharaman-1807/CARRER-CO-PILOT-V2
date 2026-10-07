from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class DSAProblem(Base):
    __tablename__ = "dsa_problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    topic = Column(String(100), nullable=False)  # Arrays, Two Pointers, Sliding Window, Hashing, Binary Search, etc.
    difficulty = Column(String(50), nullable=False)  # Easy, Medium, Hard
    description = Column(Text, nullable=False)
    starter_code = Column(Text, nullable=False)
    test_cases = Column(JSON, nullable=False, default=list)  # [{"input": ..., "expected": ...}]
    hints = Column(JSON, nullable=False, default=list)

    attempts = relationship("DSAAttempt", back_populates="problem", cascade="all, delete-orphan")


class DSAAttempt(Base):
    __tablename__ = "dsa_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("dsa_problems.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    attempt_count = Column(Integer, nullable=False, default=1)
    hints_used = Column(Integer, nullable=False, default=0)
    execution_result = Column(JSON, nullable=False, default=dict)  # passed, total, runtime, memory, error
    complexity_score = Column(Float, nullable=True)  # rating on time/space
    skill_evidence = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="dsa_attempts")
    problem = relationship("DSAProblem", back_populates="attempts")
