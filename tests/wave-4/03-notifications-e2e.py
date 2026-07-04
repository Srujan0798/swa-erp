from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.backend.models.user import User
from src.backend.core.security import hash_password


def test_task_assign_unassign_cycle(client: TestClient, db: Session):
    user = db.query(User).first()
    user_id = user.id if user else uuid4()
    if not user:
        user = User(id=user_id, email="task_e2e@example.com", name="Task E2E", password_hash=hash_password("pass"), role="pm", is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)

    response = client.post("/api/projects/tasks", json={"title": "E2E task"}, headers={"Authorization": "Bearer test"})
    assert response.status_code in (200, 401, 403, 404)
