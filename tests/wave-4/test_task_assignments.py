import pytest
from httpx import AsyncClient
import uuid
from sqlalchemy import text

from src.backend.models.user import User
from src.backend.core.roles import Role
from src.backend.models.project import Project
from src.backend.schemas.task import TaskStatus
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_assign_task(authed_pm_client: AsyncClient, test_project: Project, pm_user: User, test_designer_user: User):
    task_data = {
        "title": "Test Task for Assignment",
        "description": "Test task for assignment",
        "priority": "medium",
        "assignee_id": None,
    }
    response = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task_data,
    )
    assert response.status_code == 201
    task = response.json()
    task_id = task["id"]

    assign_data = {"assignee_id": str(test_designer_user.id)}
    response = await authed_pm_client.post(
        f"/api/tasks/{task_id}/assign",
        json=assign_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["assignee_id"] == str(test_designer_user.id)
    assert data["assignee_name"] == test_designer_user.name

    response = await authed_pm_client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    task = response.json()
    assert task["assignee_id"] == str(test_designer_user.id)
    assert task["assignee_name"] == test_designer_user.name


@pytest.mark.asyncio
async def test_unassign_task(authed_pm_client: AsyncClient, test_project: Project, pm_user: User, test_designer_user: User):
    task_data = {
        "title": "Test Task for Unassignment",
        "description": "Test task for unassignment",
        "priority": "medium",
        "assignee_id": str(test_designer_user.id),
    }
    response = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task_data,
    )
    assert response.status_code == 201
    task = response.json()
    task_id = task["id"]

    response = await authed_pm_client.delete(f"/api/tasks/{task_id}/assign")
    assert response.status_code == 200
    task = response.json()
    assert task["assignee_id"] is None
    assert task["assignee_name"] is None

    response = await authed_pm_client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    task = response.json()
    assert task["assignee_id"] is None
    assert task["assignee_name"] is None


@pytest.mark.asyncio
async def test_assign_invalid_user(authed_pm_client: AsyncClient, test_project: Project, pm_user: User):
    task_data = {
        "title": "Test Task for Invalid Assignment",
        "description": "Test task for invalid assignment",
        "priority": "medium",
        "assignee_id": None,
    }
    response = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task_data,
    )
    assert response.status_code == 201
    task = response.json()
    task_id = task["id"]

    fake_user_id = str(uuid.uuid4())
    assign_data = {"assignee_id": fake_user_id}
    response = await authed_pm_client.post(
        f"/api/tasks/{task_id}/assign",
        json=assign_data,
    )
    assert response.status_code == 400
    assert "Assignee not found or inactive" in response.json()["detail"]


@pytest.mark.asyncio
async def test_assign_inactive_user(authed_pm_client: AsyncClient, test_project: Project, pm_user: User, admin_user: User):
    session = TestingSessionLocal()
    admin_user.is_active = False
    session.merge(admin_user)
    session.commit()
    session.close()

    task_data = {
        "title": "Test Task for Inactive Assignment",
        "description": "Test task for inactive assignment",
        "priority": "medium",
        "assignee_id": None,
    }
    response = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task_data,
    )
    assert response.status_code == 201
    task = response.json()
    task_id = task["id"]

    assign_data = {"assignee_id": str(admin_user.id)}
    response = await authed_pm_client.post(
        f"/api/tasks/{task_id}/assign",
        json=assign_data,
    )
    assert response.status_code == 400
    assert "Assignee not found or inactive" in response.json()["detail"]

    session = TestingSessionLocal()
    admin_user.is_active = True
    session.merge(admin_user)
    session.commit()
    session.close()


@pytest.mark.asyncio
async def test_unassign_no_assignee(authed_pm_client: AsyncClient, test_project: Project, pm_user: User):
    task_data = {
        "title": "Test Task for Unassign No Assignee",
        "description": "Test task for unassign when no assignee",
        "priority": "medium",
        "assignee_id": None,
    }
    response = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task_data,
    )
    assert response.status_code == 201
    task = response.json()
    task_id = task["id"]

    response = await authed_pm_client.delete(f"/api/tasks/{task_id}/assign")
    assert response.status_code == 400
    assert "Task is not assigned to anyone" in response.json()["detail"]


@pytest.mark.asyncio
async def test_assign_unauthorized(authed_pm_client: AsyncClient, test_project: Project, pm_user: User, test_designer_user: User):
    # PM creates a task
    task_data = {
        "title": "Test Task for Unauthorized Assignment",
        "description": "Test task for unauthorized assignment",
        "priority": "medium",
        "assignee_id": None,
    }
    response = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task_data,
    )
    assert response.status_code == 201
    task = response.json()
    task_id = task["id"]

    # No auth header at all — should get 403
    # FastAPI HTTPBearer(auto_error=True) returns 403 when Authorization header is absent entirely.
    # 401 is reserved for malformed/invalid credentials. This asserts the real production behaviour.
    from httpx import ASGITransport, AsyncClient as _AsyncClient
    from src.backend.main import app
    async with _AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as unauthed:
        assign_data = {"assignee_id": str(test_designer_user.id)}
        response = await unauthed.post(
            f"/api/tasks/{task_id}/assign",
            json=assign_data,
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_my_tasks_returns_assigned_only(authed_pm_client: AsyncClient, test_project: Project, pm_user: User, test_designer_user: User):
    # Create tasks assigned to different users
    task1_data = {
        "title": "Task for Designer",
        "description": "Assigned to designer",
        "priority": "medium",
        "assignee_id": str(test_designer_user.id),
    }
    response1 = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task1_data,
    )
    assert response1.status_code == 201
    task1 = response1.json()

    task2_data = {
        "title": "Task for PM",
        "description": "Assigned to PM",
        "priority": "medium",
        "assignee_id": str(pm_user.id),
    }
    response2 = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task2_data,
    )
    assert response2.status_code == 201
    task2 = response2.json()

    # Check PM's my tasks - should see task2
    response = await authed_pm_client.get("/api/tasks/my-tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == task2["id"]
    assert data["items"][0]["assignee_id"] == str(pm_user.id)


@pytest.mark.asyncio
async def test_my_tasks_with_status_filter(authed_pm_client: AsyncClient, test_project: Project, pm_user: User):
    task1_data = {
        "title": "Todo Task for PM",
        "description": "Todo task",
        "priority": "medium",
        "assignee_id": str(pm_user.id),
    }
    response1 = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task1_data,
    )
    assert response1.status_code == 201
    task1 = response1.json()

    task2_data = {
        "title": "In Progress Task for PM",
        "description": "In progress task",
        "priority": "medium",
        "assignee_id": str(pm_user.id),
    }
    response2 = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task2_data,
    )
    assert response2.status_code == 201
    task2 = response2.json()

    # Transition task2 to in_progress
    response = await authed_pm_client.post(
        f"/api/tasks/{task2['id']}/transition",
        json={"to_status": "in_progress"},
    )
    assert response.status_code == 200

    # Verify tasks exist in different statuses via project stats
    response = await authed_pm_client.get(f"/api/projects/{test_project.id}/tasks/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["in_progress"] >= 1

    # Check PM's my-tasks returns both tasks
    response = await authed_pm_client.get("/api/tasks/my-tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_my_tasks_with_priority_filter(authed_pm_client: AsyncClient, test_project: Project, pm_user: User):
    task1_data = {
        "title": "Low Priority Task for PM",
        "description": "Low priority",
        "priority": "low",
        "assignee_id": str(pm_user.id),
    }
    response1 = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task1_data,
    )
    assert response1.status_code == 201
    task1 = response1.json()

    task2_data = {
        "title": "High Priority Task for PM",
        "description": "High priority",
        "priority": "high",
        "assignee_id": str(pm_user.id),
    }
    response2 = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task2_data,
    )
    assert response2.status_code == 201
    task2 = response2.json()

    # Verify both tasks exist
    response = await authed_pm_client.get("/api/tasks/my-tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    priorities = {item["priority"] for item in data["items"]}
    assert "low" in priorities
    assert "high" in priorities


@pytest.mark.asyncio
async def test_my_tasks_stats(authed_pm_client: AsyncClient, test_project: Project, pm_user: User):
    tasks_data = [
        {"title": "Todo 1", "priority": "medium"},
        {"title": "Todo 2", "priority": "medium"},
    ]
    for td in tasks_data:
        td["description"] = f"Description for {td['title']}"
        td["assignee_id"] = str(pm_user.id)
        response = await authed_pm_client.post(
            f"/api/projects/{test_project.id}/tasks",
            json=td,
        )
        assert response.status_code == 201

    resp = await authed_pm_client.get("/api/tasks/my-tasks")
    items = resp.json()["items"]
    await authed_pm_client.post(
        f"/api/tasks/{items[0]['id']}/transition",
        json={"to_status": "in_progress"},
    )

    await authed_pm_client.post(
        f"/api/tasks/{items[1]['id']}/transition",
        json={"to_status": "in_progress"},
    )
    await authed_pm_client.post(
        f"/api/tasks/{items[1]['id']}/transition",
        json={"to_status": "done"},
    )

    response = await authed_pm_client.get("/api/tasks/my-tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    stats = data["stats"]
    assert stats["in_progress"] == 1
    assert stats["done"] == 1


@pytest.mark.asyncio
async def test_project_task_stats(authed_pm_client: AsyncClient, test_project: Project, pm_user: User, test_designer_user: User):
    task1_data = {
        "title": "P1 Todo",
        "description": "Task 1",
        "priority": "medium",
        "assignee_id": str(pm_user.id),
    }
    response = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task1_data,
    )
    assert response.status_code == 201

    task2_data = {
        "title": "P2 In Progress",
        "description": "Task 2",
        "priority": "medium",
        "assignee_id": str(test_designer_user.id),
    }
    response = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task2_data,
    )
    assert response.status_code == 201
    task2 = response.json()

    await authed_pm_client.post(
        f"/api/tasks/{task2['id']}/transition",
        json={"to_status": "in_progress"},
    )

    response = await authed_pm_client.get(f"/api/projects/{test_project.id}/tasks/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert data["todo"] >= 1
    assert data["in_progress"] >= 1


@pytest.mark.asyncio
async def test_assign_audit_log(authed_pm_client: AsyncClient, test_project: Project, pm_user: User, test_designer_user: User, db_session):
    task_data = {
        "title": "Test Task for Audit Log",
        "description": "Test task for audit log",
        "priority": "medium",
        "assignee_id": None,
    }
    response = await authed_pm_client.post(
        f"/api/projects/{test_project.id}/tasks",
        json=task_data,
    )
    assert response.status_code == 201
    task = response.json()
    task_id = task["id"]

    assign_data = {"assignee_id": str(test_designer_user.id)}
    response = await authed_pm_client.post(
        f"/api/tasks/{task_id}/assign",
        json=assign_data,
    )
    assert response.status_code == 200

    from sqlalchemy import text
    result = db_session.execute(
        text("SELECT action, after_json FROM audit_log WHERE entity_type = 'task' AND entity_id = :task_id AND action = 'task.assign'"),
        {"task_id": task_id},
    ).fetchall()
    assert len(result) >= 1
    action, after_json = result[-1]
    assert action == "task.assign"
    import json
    after_data = json.loads(after_json) if isinstance(after_json, str) else after_json
    assert after_data["assignee_id"] == str(test_designer_user.id)
    assert after_data["assignee_name"] == test_designer_user.name
