import pytest
from httpx import AsyncClient
from src.backend.core.lifecycle import ProjectStatus, can_transition

pytestmark = pytest.mark.asyncio


async def test_allowed_transitions():
    assert can_transition(ProjectStatus.LEAD, ProjectStatus.QUOTE)
    assert can_transition(ProjectStatus.QUOTE, ProjectStatus.AWARDED)
    assert not can_transition(ProjectStatus.LEAD, ProjectStatus.CLOSED)
    assert not can_transition(ProjectStatus.CLOSED, ProjectStatus.LEAD)


async def test_transition_lead_to_quote(authed_pm_client, db_session):
    from src.backend.models.client import Client
    from src.backend.models.project import Project

    client = Client(name="LifecycleClient", code="LC-001", primary_email="lc@example.com")
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)

    project = Project(
        client_id=client.id,
        name="LifecycleProj",
        code="TL-001",
        status="Lead",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    r = await authed_pm_client.post(f"/api/projects/{project.id}/transition", json={
        "to_status": "Quote"
    })
    assert r.status_code == 200
    assert r.json()["status"] == "Quote"


async def test_invalid_transition_returns_400(authed_pm_client, db_session):
    from src.backend.models.client import Client
    from src.backend.models.project import Project

    client = Client(name="BadClient", code="BC-001", primary_email="bc@example.com")
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)

    project = Project(
        client_id=client.id,
        name="BadProj",
        code="TB-001",
        status="Lead",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    r = await authed_pm_client.post(f"/api/projects/{project.id}/transition", json={
        "to_status": "Closed"
    })
    assert r.status_code == 400


async def test_direct_status_patch_rejected(authed_admin_client, db_session):
    from src.backend.models.client import Client
    from src.backend.models.project import Project

    client = Client(name="PatchClient", code="PC-002", primary_email="pc2@example.com")
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)

    project = Project(
        client_id=client.id,
        name="PatchProj",
        code="TP-001",
        status="Lead",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    r = await authed_admin_client.patch(f"/api/projects/{project.id}", json={"status": "Quote"})
    assert r.status_code == 400


async def test_closed_sets_actual_end_date(authed_pm_client, db_session):
    from src.backend.models.client import Client
    from src.backend.models.project import Project

    client = Client(name="CloseClient", code="CC-001", primary_email="cc@example.com")
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)

    project = Project(
        client_id=client.id,
        name="CloseProj",
        code="TC-001",
        status="Lead",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    for s in ["Quote", "Awarded", "Design", "Vendor", "Execution", "Validation"]:
        await authed_pm_client.post(f"/api/projects/{project.id}/transition", json={"to_status": s})

    r = await authed_pm_client.post(f"/api/projects/{project.id}/transition", json={"to_status": "Closed"})
    assert r.status_code == 200
    assert r.json()["actual_end_date"] is not None