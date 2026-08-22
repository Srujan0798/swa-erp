"""Wave 33 — task_service coverage.

Tests every public function in src/backend/services/task_service.py:
create, get, list, list_my, update, delete, comment, counts,
transition, reorder, bulk_status, assign, unassign, project_stats.
"""
from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import select

from src.backend.core.task_workflow import VALID_TRANSITIONS
from src.backend.models.task import Task, TaskComment
from src.backend.models.user import User
from src.backend.schemas.task import TaskCreate, TaskPriority, TaskUpdate
from src.backend.services.task_service import (
    add_comment_service,
    assign_task_service,
    bulk_update_status_service,
    create_task_service,
    delete_task_service,
    get_project_task_stats_service,
    get_task_counts_service,
    get_task_service,
    list_my_tasks_service,
    list_tasks_service,
    reorder_task_service,
    transition_task_service,
    unassign_task_service,
    update_task_service,
)


@pytest.fixture
def reporter(db_session):
    u = User(
        email="reporter@swa.co.in",
        name="Reporter",
        password_hash="x",
        role="pm",
    )
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def assignee(db_session):
    u = User(
        email="assignee@swa.co.in",
        name="Assignee",
        password_hash="x",
        role="designer",
    )
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def project(test_project):
    return test_project


@pytest.fixture
def task(db_session, project, reporter):
    t = Task(
        project_id=project.id,
        title="Test Task",
        description="A test task",
        status="todo",
        priority=2,
        reporter_id=reporter.id,
    )
    db_session.add(t)
    db_session.flush()
    return t


# ---- create_task_service ----

def test_create_task_happy(db_session, project, reporter):
    body = TaskCreate(title="New Task", priority=TaskPriority.HIGH)
    result = create_task_service(db_session, project.id, body, reporter.id)
    assert result.title == "New Task"
    assert result.status == "todo"
    assert result.priority == "high"
    assert result.created_by == reporter.id


def test_create_task_with_assignee(db_session, project, reporter, assignee):
    body = TaskCreate(title="Assigned", assignee_id=assignee.id)
    result = create_task_service(db_session, project.id, body, reporter.id)
    assert result.assignee_id == assignee.id
    assert result.assignee_name == "Assignee"


def test_create_task_invalid_assignee_raises(db_session, project, reporter):
    body = TaskCreate(title="Bad Assign", assignee_id=uuid.uuid4())
    with pytest.raises(Exception, match="Assignee not found"):
        create_task_service(db_session, project.id, body, reporter.id)


def test_create_task_inactive_assignee_raises(db_session, project, reporter):
    u = User(
        email="inactive@swa.co.in",
        name="Inactive",
        password_hash="x",
        role="viewer",
        is_active=False,
    )
    db_session.add(u)
    db_session.flush()
    body = TaskCreate(title="Inactive Assign", assignee_id=u.id)
    with pytest.raises(Exception, match="Assignee not found"):
        create_task_service(db_session, project.id, body, reporter.id)


# ---- get_task_service ----

def test_get_task_exists(db_session, task):
    result = get_task_service(db_session, task.id)
    assert result is not None
    assert result.title == "Test Task"


def test_get_task_not_exists(db_session):
    result = get_task_service(db_session, uuid.uuid4())
    assert result is None


# ---- list_tasks_service ----

def test_list_tasks_by_project(db_session, project, task):
    items, total, page, page_size = list_tasks_service(db_session, project.id)
    assert total >= 1
    assert any(i.title == "Test Task" for i in items)


def test_list_tasks_filter_status(db_session, project, task):
    items, total, _, _ = list_tasks_service(db_session, project.id, status="todo")
    assert all(i.status == "todo" for i in items)


def test_list_tasks_filter_assignee(db_session, project, task, assignee):
    task.assignee_id = assignee.id
    db_session.flush()
    items, total, _, _ = list_tasks_service(db_session, project.id, assignee_id=assignee.id)
    assert any(i.assignee_id == assignee.id for i in items)


def test_list_tasks_filter_priority(db_session, project, task):
    items, total, _, _ = list_tasks_service(db_session, project.id, priority="medium")
    assert total >= 1


# ---- list_my_tasks_service ----

def test_list_my_tasks(db_session, project, task, assignee):
    task.assignee_id = assignee.id
    db_session.flush()
    result = list_my_tasks_service(db_session, assignee.id)
    assert result.total >= 1
    assert result.stats.total >= 1


def test_list_my_tasks_empty(db_session):
    result = list_my_tasks_service(db_session, uuid.uuid4())
    assert result.total == 0
    assert result.stats.todo == 0


# ---- update_task_service ----

def test_update_task_title(db_session, task, reporter):
    body = TaskUpdate(title="Updated Title")
    result = update_task_service(db_session, task.id, body, reporter.id)
    assert result is not None
    assert result.title == "Updated Title"


def test_update_task_priority(db_session, task, reporter):
    body = TaskUpdate(priority=TaskPriority.CRITICAL)
    result = update_task_service(db_session, task.id, body, reporter.id)
    assert result is not None
    assert result.priority == "critical"


def test_update_task_not_found(db_session, reporter):
    body = TaskUpdate(title="X")
    result = update_task_service(db_session, uuid.uuid4(), body, reporter.id)
    assert result is None


# ---- delete_task_service ----

def test_delete_task(db_session, task, reporter):
    ok = delete_task_service(db_session, task.id, reporter.id)
    assert ok is True
    assert get_task_service(db_session, task.id) is None


def test_delete_task_not_found(db_session, reporter):
    ok = delete_task_service(db_session, uuid.uuid4(), reporter.id)
    assert ok is False


# ---- add_comment_service ----

def test_add_comment(db_session, task, reporter):
    result = add_comment_service(db_session, task.id, reporter.id, "Great work!")
    assert result is not None
    assert result.content == "Great work!"
    assert result.user_id == reporter.id


def test_add_comment_task_not_found(db_session, reporter):
    result = add_comment_service(db_session, uuid.uuid4(), reporter.id, "x")
    assert result is None


# ---- get_task_counts_service ----

def test_get_task_counts(db_session, project, task):
    counts = get_task_counts_service(db_session, project.id)
    assert counts["todo"] >= 1
    assert counts["total"] >= 1


# ---- transition_task_service ----

def test_transition_todo_to_in_progress(db_session, task, reporter):
    result = transition_task_service(db_session, task.id, "in_progress", reporter.id)
    assert result is not None
    assert result.status == "in_progress"


def test_transition_in_progress_to_done(db_session, task, reporter):
    task.status = "in_progress"
    db_session.flush()
    result = transition_task_service(db_session, task.id, "done", reporter.id)
    assert result is not None
    assert result.status == "done"


def test_transition_invalid_raises(db_session, task, reporter):
    with pytest.raises(ValueError, match="Invalid transition"):
        transition_task_service(db_session, task.id, "done", reporter.id)


def test_transition_not_found(db_session, reporter):
    result = transition_task_service(db_session, uuid.uuid4(), "in_progress", reporter.id)
    assert result is None


# ---- reorder_task_service ----

def test_reorder_task(db_session, task, reporter):
    result = reorder_task_service(db_session, task.id, "in_progress", 5, reporter.id)
    assert result is not None
    assert result.status == "in_progress"
    assert result.sort_order == 5


def test_reorder_task_not_found(db_session, reporter):
    result = reorder_task_service(db_session, uuid.uuid4(), "todo", 0, reporter.id)
    assert result is None


def test_reorder_task_invalid_transition_raises(db_session, task, reporter):
    with pytest.raises(ValueError, match="Invalid transition"):
        reorder_task_service(db_session, task.id, "done", 0, reporter.id)


# ---- bulk_update_status_service ----

def test_bulk_update_status(db_session, project, reporter):
    t1 = Task(project_id=project.id, title="T1", status="todo", priority=2, reporter_id=reporter.id)
    t2 = Task(project_id=project.id, title="T2", status="todo", priority=2, reporter_id=reporter.id)
    db_session.add_all([t1, t2])
    db_session.flush()
    count = bulk_update_status_service(db_session, [t1.id, t2.id], "in_progress", reporter.id)
    assert count == 2


def test_bulk_update_invalid_transition_raises(db_session, task, reporter):
    with pytest.raises(ValueError, match="Invalid transition"):
        bulk_update_status_service(db_session, [task.id], "done", reporter.id)


# ---- assign_task_service ----

def test_assign_task(db_session, task, reporter, assignee):
    result = assign_task_service(db_session, task.id, assignee.id, reporter.id)
    assert result is not None
    assert result.assignee_id == assignee.id


def test_assign_task_not_found(db_session, reporter, assignee):
    result = assign_task_service(db_session, uuid.uuid4(), assignee.id, reporter.id)
    assert result is None


def test_assign_task_assignee_not_found(db_session, task, reporter):
    result = assign_task_service(db_session, task.id, uuid.uuid4(), reporter.id)
    assert result is None


# ---- unassign_task_service ----

def test_unassign_task(db_session, task, reporter, assignee):
    task.assignee_id = assignee.id
    db_session.flush()
    result = unassign_task_service(db_session, task.id, reporter.id)
    assert result is not None
    assert result.assignee_id is None


def test_unassign_task_not_found(db_session, reporter):
    result = unassign_task_service(db_session, uuid.uuid4(), reporter.id)
    assert result is None


def test_unassign_task_already_unassigned(db_session, task, reporter):
    result = unassign_task_service(db_session, task.id, reporter.id)
    assert result is None


# ---- get_project_task_stats_service ----

def test_project_task_stats(db_session, project, task):
    stats = get_project_task_stats_service(db_session, project.id)
    assert stats.todo >= 1
    assert stats.total >= 1
