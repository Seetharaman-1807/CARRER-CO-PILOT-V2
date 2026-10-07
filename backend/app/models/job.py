from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class TargetRole(Base):
    __tablename__ = "target_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_name = Column(String(100), nullable=False)
    is_primary = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="target_roles")
    job_descriptions = relationship("JobDescription", back_populates="target_role", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="target_role", cascade="all, delete-orphan")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role_id = Column(Integer, ForeignKey("target_roles.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    parsed_requirements = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="job_descriptions")
    target_role = relationship("TargetRole", back_populates="job_descriptions")
    requirements = relationship("RoleRequirement", back_populates="job_description", cascade="all, delete-orphan")
    ats_analyses = relationship("ATSAnalysis", back_populates="job_description", cascade="all, delete-orphan")


class RoleRequirement(Base):
    __tablename__ = "role_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    canonical_skill = Column(String(100), nullable=False)
    requirement_type = Column(String(50), nullable=False, default="required")  # required, preferred
    importance = Column(Float, nullable=False, default=1.0)
    evidence = Column(Text, nullable=True)

    job_description = relationship("JobDescription", back_populates="requirements")


class ATSAnalysis(Base):
    __tablename__ = "ats_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)
    scoring_version = Column(String(50), nullable=False, default="v2.0-deterministic")
    component_scores = Column(JSON, nullable=False, default=dict)  # keyword, technical, experience, education, etc.
    feedback = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="ats_analyses")
    resume_version = relationship("ResumeVersion", back_populates="ats_analyses")
    job_description = relationship("JobDescription", back_populates="ats_analyses")


class SkillGapAnalysis(Base):
    __tablename__ = "skill_gap_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role_id = Column(Integer, ForeignKey("target_roles.id", ondelete="SET NULL"), nullable=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True)
    gaps = Column(JSON, nullable=False, default=list)  # missing, weak, related, exact
    summary = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="skill_gaps")


class ReadinessSnapshot(Base):
    __tablename__ = "readiness_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role_id = Column(Integer, ForeignKey("target_roles.id", ondelete="SET NULL"), nullable=True)
    overall_score = Column(Float, nullable=False)
    component_scores = Column(JSON, nullable=False, default=dict)  # resume_quality, technical_skills, dsa, etc.
    confidence = Column(String(50), nullable=False, default="Medium")
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="readiness_snapshots")


class CareerFitResult(Base):
    __tablename__ = "career_fit_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_name = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    evidence = Column(JSON, nullable=False, default=list)
    skill_gaps = Column(JSON, nullable=False, default=list)
    confidence = Column(String(50), nullable=False, default="Medium")
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="career_fits")
