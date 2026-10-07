from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role_id = Column(Integer, ForeignKey("target_roles.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="active")  # active, completed, archived
    goal = Column(Text, nullable=True)
    weekly_plan = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="roadmaps")
    target_role = relationship("TargetRole", back_populates="roadmaps")
    tasks = relationship("RoadmapTask", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapTask.id")


class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(50), nullable=False, default="Medium")  # High, Medium, Low
    estimated_minutes = Column(Integer, nullable=False, default=45)
    status = Column(String(50), nullable=False, default="pending")  # pending, completed
    due_date = Column(DateTime, nullable=True)
    completion_criteria = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    roadmap = relationship("Roadmap", back_populates="tasks")
