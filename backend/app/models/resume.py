from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="Default Resume")
    current_version_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="resumes")
    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan", order_by="ResumeVersion.version_number.desc()")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    file_name = Column(String(255), nullable=False)
    file_reference = Column(String(500), nullable=True)
    parsed_content = Column(JSON, nullable=False, default=dict)
    raw_text = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=utc_now, nullable=False)

    resume = relationship("Resume", back_populates="versions")
    evidence = relationship("ResumeEvidence", back_populates="resume_version", cascade="all, delete-orphan")
    ats_analyses = relationship("ATSAnalysis", back_populates="resume_version", cascade="all, delete-orphan")


class ResumeEvidence(Base):
    __tablename__ = "resume_evidence"

    id = Column(Integer, primary_key=True, index=True)
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # skill, project, education, certification
    entity_value = Column(String(255), nullable=False)
    evidence_text = Column(Text, nullable=False)
    section = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)

    resume_version = relationship("ResumeVersion", back_populates="evidence")
