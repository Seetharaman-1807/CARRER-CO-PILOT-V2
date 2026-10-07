from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False)  # Languages, Frameworks, Databases, Systems, DSA, etc.
    parent_skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    aliases = Column(JSON, nullable=False, default=list)  # e.g. ["postgres", "postgresql", "psql"]

    parent = relationship("Skill", remote_side=[id], backref="children")
    candidate_skills = relationship("CandidateSkill", back_populates="skill")


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True, index=True)
    canonical_name = Column(String(100), nullable=False, index=True)
    score = Column(Float, nullable=False, default=0.0)  # 0 to 100
    confidence = Column(String(50), nullable=False, default="Low")  # Low, Medium, High
    target_score = Column(Float, nullable=False, default=75.0)
    trend = Column(String(50), nullable=False, default="Stable")  # Improving, Stable, Regressing
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="candidate_skills")
    skill = relationship("Skill", back_populates="candidate_skills")
    evidence_items = relationship("SkillEvidence", back_populates="candidate_skill", cascade="all, delete-orphan", order_by="SkillEvidence.created_at.desc()")


class SkillEvidence(Base):
    __tablename__ = "skill_evidence"

    id = Column(Integer, primary_key=True, index=True)
    candidate_skill_id = Column(Integer, ForeignKey("candidate_skills.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # "resume", "dsa", "interview", "project", "assessment"
    source_id = Column(String(100), nullable=True)  # reference id
    score = Column(Float, nullable=False)  # observed score (0 - 100)
    confidence = Column(Float, nullable=False, default=0.8)  # 0.0 - 1.0 weight
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    candidate_skill = relationship("CandidateSkill", back_populates="evidence_items")
