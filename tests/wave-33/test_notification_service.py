"""Wave 33 — notification_service coverage.

Tests every method of NotificationService: emit, task_assigned,
status_changed, task_commented. Also covers NotificationRepository
methods exercised through the service.
"""
from __future__ import annotations

import uuid

import pytest

from src.backend.models.notification import Notification
from src.backend.models.task import Task
from src.backend.models.user import User
from src.backend.schemas.notification import NotificationType
from src.backend.services.notification_service import NotificationService


@pytest.fixture
def user_a(db_session):
    u = User(email="alice@swa.co.in", name="Alice", password_hash="x", role="pm")
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def user_b(db_session):
    u = User(email="bob@swa.co.in", name="Bob", password_hash="x", role="designer")
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def task(db_session, test_project, user_a, user_b):
    t = Task(
        project_id=test_project.id,
        title="Design Review",
        status="todo",
        priority=2,
        reporter_id=user_a.id,
        assignee_id=user_b.id,
    )
    db_session.add(t)
    db_session.flush()
    return t


# ---- emit ----

def test_emit_creates_notification(db_session, user_a):
    svc = NotificationService(db_session)
    n = svc.emit(
        user_a.id,
        NotificationType.TASK_ASSIGNED,
        "Hello",
        "Body message",
        reference_type="task",
        reference_id=uuid.uuid4(),
    )
    assert n is not None
    assert n.title == "Hello"
    assert n.message == "Body message"
    assert n.user_id == user_a.id
    assert n.is_read is False


def test_emit_without_reference(db_session, user_a):
    svc = NotificationService(db_session)
    n = svc.emit(user_a.id, NotificationType.TASK_DUE_SOON, "Due soon", "Task is due")
    assert n.reference_type is None
    assert n.reference_id is None


def test_emit_stores_string_type(db_session, user_a):
    svc = NotificationService(db_session)
    n = svc.emit(user_a.id, NotificationType.TASK_OVERDUE, "Overdue", "Past due")
    assert n.type == "task_overdue"


# ---- task_assigned ----

def test_task_assigned(db_session, task, user_a, user_b):
    svc = NotificationService(db_session)
    svc.task_assigned(task, assignee=user_b, actor=user_a)
    notifs = db_session.query(Notification).filter(Notification.user_id == user_b.id).all()
    assert len(notifs) == 1
    assert notifs[0].type == NotificationType.TASK_ASSIGNED.value
    assert "assigned you" in notifs[0].message
    assert notifs[0].reference_type == "task"
    assert notifs[0].reference_id == task.id


# ---- status_changed ----

def test_status_changed_notifies_both_assignee_and_reporter(db_session, task, user_a, user_b):
    svc = NotificationService(db_session)
    task.status = "in_progress"
    db_session.flush()
    svc.status_changed(task, actor=user_a)
    notifs = db_session.query(Notification).all()
    recipients = {n.user_id for n in notifs}
    assert user_a.id in recipients
    assert user_b.id in recipients
    assert all(n.type == NotificationType.TASK_STATUS_CHANGED.value for n in notifs)


def test_status_changed_skips_none_users(db_session, test_project, user_a):
    t = Task(
        project_id=test_project.id,
        title="No Assignee",
        status="todo",
        priority=2,
        reporter_id=user_a.id,
        assignee_id=None,
    )
    db_session.add(t)
    db_session.flush()
    svc = NotificationService(db_session)
    t.status = "in_progress"
    db_session.flush()
    svc.status_changed(t, actor=user_a)
    notifs = db_session.query(Notification).filter(Notification.user_id == user_a.id).all()
    assert len(notifs) == 1


def test_status_changed_deduplicates_same_user_as_both(db_session, test_project, user_a):
    t = Task(
        project_id=test_project.id,
        title="Self Assigned",
        status="todo",
        priority=2,
        reporter_id=user_a.id,
        assignee_id=user_a.id,
    )
    db_session.add(t)
    db_session.flush()
    svc = NotificationService(db_session)
    t.status = "done"
    db_session.flush()
    svc.status_changed(t, actor=user_a)
    notifs = db_session.query(Notification).filter(Notification.user_id == user_a.id).all()
    assert len(notifs) == 1


# ---- task_commented ----

def test_task_commented_notifies_both(db_session, task, user_a, user_b):
    svc = NotificationService(db_session)
    svc.task_commented(task, actor=user_a)
    notifs = db_session.query(Notification).all()
    recipients = {n.user_id for n in notifs}
    assert user_a.id in recipients
    assert user_b.id in recipients
    assert all(n.type == NotificationType.TASK_COMMENT.value for n in notifs)


def test_task_commented_skips_none_users(db_session, test_project, user_a):
    t = Task(
        project_id=test_project.id,
        title="No Assignee",
        status="todo",
        priority=2,
        reporter_id=user_a.id,
        assignee_id=None,
    )
    db_session.add(t)
    db_session.flush()
    svc = NotificationService(db_session)
    svc.task_commented(t, actor=user_a)
    notifs = db_session.query(Notification).filter(Notification.user_id == user_a.id).all()
    assert len(notifs) == 1


def test_task_commented_deduplicates_same_user(db_session, test_project, user_a):
    t = Task(
        project_id=test_project.id,
        title="Self Assigned",
        status="todo",
        priority=2,
        reporter_id=user_a.id,
        assignee_id=user_a.id,
    )
    db_session.add(t)
    db_session.flush()
    svc = NotificationService(db_session)
    svc.task_commented(t, actor=user_a)
    notifs = db_session.query(Notification).filter(Notification.user_id == user_a.id).all()
    assert len(notifs) == 1
