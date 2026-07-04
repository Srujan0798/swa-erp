import pytest
from uuid import uuid4
from datetime import datetime, timedelta

# Wave-4 Contract Tests — Task Management
# Run: pytest .specify/specs/wave-4/contracts/ -v

class TestTasksAPI:
    """Task CRUD API contracts."""

    def test_create_task_minimal(self, client, pm_token, project_id):
        """Create task with minimal fields."""
        r = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Review BOQ"},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "Review BOQ"
        assert data["status"] == "todo"
        assert data["project_id"] == str(project_id)
        assert "id" in data
        assert data["version"] == 1

    def test_create_task_full(self, client, pm_token, project_id, designer_id):
        """Create task with all fields."""
        due = (datetime.utcnow() + timedelta(days=7)).isoformat()
        r = client.post(
            f"/api/projects/{project_id}/tasks",
            json={
                "title": "Prepare DBR",
                "description": "Design Basis Report for thermal audit",
                "assignee_id": str(designer_id),
                "due_date": due,
                "priority": 2,
                "estimated_hours": 4.5
            },
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 201
        data = r.json()
        assert data["assignee_id"] == str(designer_id)
        assert data["priority"] == 2
        assert data["estimated_hours"] == 4.5

    def test_create_task_forbidden_viewer(self, client, viewer_token, project_id):
        """Viewer cannot create tasks."""
        r = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Nope"},
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert r.status_code == 403

    def test_get_task(self, client, pm_token, project_id):
        """Get task by ID."""
        create = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Get Me"},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        task_id = create.json()["id"]
        r = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 200
        assert r.json()["title"] == "Get Me"

    def test_list_tasks_filters(self, client, pm_token, project_id):
        """List tasks with filters."""
        # Create tasks with different statuses
        for status in ["todo", "in_progress", "review", "done"]:
            client.post(
                f"/api/projects/{project_id}/tasks",
                json={"title": f"Task {status}", "status": status},
                headers={"Authorization": f"Bearer {pm_token}"}
            )
        # Filter by status
        r = client.get(
            f"/api/projects/{project_id}/tasks?status=done",
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 200
        tasks = r.json()
        assert all(t["status"] == "done" for t in tasks)
        assert len(tasks) == 1

    def test_update_task_optimistic_lock(self, client, pm_token, project_id):
        """Optimistic lock prevents lost updates."""
        create = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Lock Me"},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        task = create.json()
        task_id = task["id"]
        version = task["version"]

        # First update succeeds
        r1 = client.patch(
            f"/api/tasks/{task_id}",
            json={"title": "Updated", "version": version},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r1.status_code == 200
        assert r1.json()["version"] == version + 1

        # Second update with stale version fails
        r2 = client.patch(
            f"/api/tasks/{task_id}",
            json={"title": "Stale", "version": version},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r2.status_code == 409

    def test_delete_task(self, client, pm_token, project_id):
        """Delete task."""
        create = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Delete Me"},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        task_id = create.json()["id"]
        r = client.delete(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 204
        # Verify gone
        r2 = client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r2.status_code == 404


class TestTaskDependencies:
    """Task dependency DAG contracts."""

    def test_add_dependency(self, client, pm_token, project_id):
        """Add dependency: task B depends on task A."""
        a = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Task A"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()
        b = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Task B"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        r = client.post(
            f"/api/tasks/{b['id']}/dependencies",
            json={"depends_on_task_id": a["id"]},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 201
        dep = r.json()
        assert dep["task_id"] == b["id"]
        assert dep["depends_on_task_id"] == a["id"]

    def test_cycle_detection(self, client, pm_token, project_id):
        """Cycle detection rejects circular dependency."""
        a = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "A"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()
        b = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "B"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()
        c = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "C"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        # A -> B
        client.post(
            f"/api/tasks/{b['id']}/dependencies",
            json={"depends_on_task_id": a["id"]},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        # B -> C
        client.post(
            f"/api/tasks/{c['id']}/dependencies",
            json={"depends_on_task_id": b["id"]},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        # C -> A (creates cycle) -> should fail
        r = client.post(
            f"/api/tasks/{a['id']}/dependencies",
            json={"depends_on_task_id": c["id"]},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 400
        assert "cycle" in r.json()["detail"].lower()

    def test_blocked_status(self, client, pm_token, project_id):
        """Task with unfinished dependency cannot move to in_progress."""
        a = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "A"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()
        b = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "B"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        # B depends on A
        client.post(
            f"/api/tasks/{b['id']}/dependencies",
            json={"depends_on_task_id": a["id"]},
            headers={"Authorization": f"Bearer {pm_token}"}
        )

        # Try to move B to in_progress while A is todo -> should fail
        r = client.patch(
            f"/api/tasks/{b['id']}",
            json={"status": "in_progress", "version": 1},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 400
        assert "blocked" in r.json()["detail"].lower()

        # Complete A, then B can move
        client.patch(
            f"/api/tasks/{a['id']}",
            json={"status": "done", "version": 1},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        r2 = client.patch(
            f"/api/tasks/{b['id']}",
            json={"status": "in_progress", "version": 1},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r2.status_code == 200
        assert r2.json()["status"] == "in_progress"

    def test_list_dependencies(self, client, pm_token, project_id):
        """List direct and transitive dependencies."""
        a = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "A"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()
        b = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "B"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()
        c = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "C"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        # A -> B -> C
        client.post(
            f"/api/tasks/{b['id']}/dependencies",
            json={"depends_on_task_id": a["id"]},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        client.post(
            f"/api/tasks/{c['id']}/dependencies",
            json={"depends_on_task_id": b["id"]},
            headers={"Authorization": f"Bearer {pm_token}"}
        )

        # Direct deps of C
        r = client.get(
            f"/api/tasks/{c['id']}/dependencies",
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 200
        deps = r.json()
        assert len(deps) == 1
        assert deps[0]["depends_on_task_id"] == b["id"]

        # Transitive? (optional endpoint)
        # GET /api/tasks/{c['id']}/dependencies?transitive=true


class TestTaskComments:
    """Task comments & threading contracts."""

    def test_add_comment(self, client, pm_token, project_id, designer_id):
        """Add top-level comment."""
        task = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Commentable"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        r = client.post(
            f"/api/tasks/{task['id']}/comments",
            json={"content": "Please review"},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 201
        c = r.json()
        assert c["content"] == "Please review"
        assert c["author_id"] == pm_token  # or user_id from token
        assert c["parent_comment_id"] is None

    def test_threaded_reply(self, client, pm_token, project_id, designer_id):
        """Reply to a comment."""
        task = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Threaded"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        parent = client.post(
            f"/api/tasks/{task['id']}/comments",
            json={"content": "Parent"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        r = client.post(
            f"/api/tasks/{task['id']}/comments",
            json={"content": "Reply", "parent_comment_id": parent["id"]},
            headers={"Authorization": f"Bearer {designer_id}"}
        )
        assert r.status_code == 201
        reply = r.json()
        assert reply["parent_comment_id"] == parent["id"]

    def test_list_comments(self, client, pm_token, project_id):
        """List comments for a task (flat or threaded)."""
        task = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "List Comments"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        for i in range(3):
            client.post(
                f"/api/tasks/{task['id']}/comments",
                json={"content": f"Comment {i}"},
                headers={"Authorization": f"Bearer {pm_token}"}
            )

        r = client.get(
            f"/api/tasks/{task['id']}/comments",
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 200
        comments = r.json()
        assert len(comments) == 3


class TestKanban:
    """Kanban board contracts."""

    def test_kanban_board_structure(self, client, pm_token, project_id):
        """Kanban endpoint returns columns grouped by status."""
        # Create tasks in different statuses
        for status in ["todo", "in_progress", "review", "done"]:
            client.post(
                f"/api/projects/{project_id}/tasks",
                json={"title": f"Task {status}", "status": status},
                headers={"Authorization": f"Bearer {pm_token}"}
            )

        r = client.get(
            f"/api/projects/{project_id}/tasks/kanban",
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 200
        board = r.json()
        assert set(board.keys()) == {"todo", "in_progress", "review", "done"}
        assert len(board["todo"]) == 1
        assert len(board["done"]) == 1

    def test_reorder_within_column(self, client, pm_token, project_id):
        """Reorder tasks within same column (position update)."""
        tasks = []
        for i in range(3):
            t = client.post(
                f"/api/projects/{project_id}/tasks",
                json={"title": f"Task {i}", "status": "todo"},
                headers={"Authorization": f"Bearer {pm_token}"}
            ).json()
            tasks.append(t)

        # Move task 2 to position 0
        r = client.patch(
            f"/api/tasks/{tasks[2]['id']}/reorder",
            json={"status": "todo", "position": 0},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 200
        assert r.json()["position"] == 0

        # Verify order
        r2 = client.get(
            f"/api/projects/{project_id}/tasks/kanban",
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        todo = r2.json()["todo"]
        assert todo[0]["id"] == tasks[2]["id"]

    def test_move_between_columns(self, client, pm_token, project_id):
        """Drag task from todo to in_progress."""
        task = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Move Me", "status": "todo"},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        r = client.patch(
            f"/api/tasks/{task['id']}/reorder",
            json={"status": "in_progress", "position": 0},
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 200
        assert r.json()["status"] == "in_progress"
        assert r.json()["position"] == 0


class TestTaskNotifications:
    """Notification contracts (in-app + email)."""

    def test_notification_on_assignment(self, client, pm_token, project_id, designer_id):
        """Notification created when task assigned."""
        task = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Notify Me", "assignee_id": designer_id},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        r = client.get(
            f"/api/notifications?user_id={designer_id}",
            headers={"Authorization": f"Bearer {designer_id}"}
        )
        assert r.status_code == 200
        notifs = r.json()
        assert any(n["type"] == "task_assigned" for n in notifs)

    def test_notification_on_status_change(self, client, pm_token, project_id, designer_id):
        """Notification on status change for assignee."""
        task = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Status Change", "assignee_id": designer_id},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        client.patch(
            f"/api/tasks/{task['id']}",
            json={"status": "in_progress", "version": 1},
            headers={"Authorization": f"Bearer {pm_token}"}
        )

        r = client.get(
            f"/api/notifications?user_id={designer_id}",
            headers={"Authorization": f"Bearer {designer_id}"}
        )
        notifs = r.json()
        assert any(n["type"] == "task_status_changed" for n in notifs)

    def test_due_soon_notification(self, client, pm_token, project_id, designer_id):
        """Notification sent for due-soon tasks (via Celery beat)."""
        due = (datetime.utcnow() + timedelta(hours=12)).isoformat()
        task = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Due Soon", "assignee_id": designer_id, "due_date": due},
            headers={"Authorization": f"Bearer {pm_token}"}
        ).json()

        # Trigger the due-soon check (normally Celery beat)
        # This tests the endpoint that Celery calls
        r = client.post(
            "/api/internal/check-due-soon",
            headers={"Authorization": f"Bearer {pm_token}"}
        )
        assert r.status_code == 200

        notifs = client.get(
            f"/api/notifications?user_id={designer_id}",
            headers={"Authorization": f"Bearer {designer_id}"}
        ).json()
        assert any(n["type"] == "task_due_soon" for n in notifs)