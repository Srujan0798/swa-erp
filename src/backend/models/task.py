import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    ForeignKey,
    DateTime,
    DECIMAL,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.backend.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="todo", index=True)
    priority = Column(Integer, default=0, nullable=False)
    assignee_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    reporter_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    due_date = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    estimated_hours = Column(DECIMAL(6, 2), nullable=True)
    actual_hours = Column(DECIMAL(6, 2), nullable=False, default=0)
    position = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", foreign_keys=[project_id], back_populates="tasks", lazy="selectin")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks", lazy="selectin")
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_tasks", lazy="selectin")
    dependencies = relationship("TaskDependency", foreign_keys="TaskDependency.task_id", back_populates="task", cascade="all, delete-orphan", lazy="selectin")
    dependents = relationship("TaskDependency", foreign_keys="TaskDependency.depends_on_task_id", back_populates="depends_on_task", cascade="all, delete-orphan", lazy="selectin")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("ix_tasks_project_status", "project_id", "status"),
        Index("ix_tasks_assignee_status", "assignee_id", "status"),
    )


class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    task_id = Column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    depends_on_task_id = Column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    task = relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    depends_on_task = relationship("Task", foreign_keys=[depends_on_task_id], back_populates="dependents")


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    parent_comment_id = Column(
        UUID(as_uuid=True), ForeignKey("task_comments.id", ondelete="CASCADE"), nullable=True
    )
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="authored_task_comments")
    parent = relationship("TaskComment", remote_side=[id], back_populates="replies")
    replies = relationship("TaskComment", back_populates="parent")
