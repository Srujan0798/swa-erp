"""Tests for Invoicing (Task 03)."""

from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

import pytest

from src.backend.models.audit_log import AuditLog
from src.backend.models.client import Client
from src.backend.models.invoice import Invoice
from src.backend.models.project import Project
from src.backend.models.time_tracking import TimeEntry
from src.backend.services.invoice_service import generate_from_time_entries

pytestmark = pytest.mark.asyncio


async def _setup_project(authed_admin_client):
    """Helper: create a client and project, return project_id."""
    r = await authed_admin_client.post(
        "/api/clients",
        json={"name": "Inv Client", "code": "INVC-01", "primary_email": "invc@test.com"},
    )
    assert r.status_code == 201
    client_id = r.json()["id"]

    r2 = await authed_admin_client.post(
        "/api/projects",
        json={
            "client_id": str(client_id),
            "name": "Invoice Project",
            "code": "INVP-01",
            "status": "Lead",
        },
    )
    assert r2.status_code == 201
    return r2.json()["id"]


async def test_create_invoice_with_items(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "due_date": (date.today() + timedelta(days=30)).isoformat(),
            "notes": "Test invoice",
            "tax_rate": "18.00",
            "items": [
                {"description": "Design services", "quantity": "10.00", "rate": "5000.00"},
                {"description": "Development", "quantity": "20.00", "rate": "5000.00"},
            ],
        },
    )
    assert r.status_code == 201
    inv = r.json()
    assert inv["status"] == "draft"
    assert inv["currency"] == "INR"
    assert float(inv["subtotal"]) == 150000.00  # (10+20)*5000
    assert float(inv["tax_rate"]) == 18.00
    assert float(inv["tax_amount"]) == 27000.00  # 150000 * 18/100
    assert float(inv["total"]) == 177000.00  # 150000 + 27000


async def test_invoice_number_auto_generate(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item 1", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    assert r.status_code == 201
    inv_num = r.json()["invoice_number"]
    # Should match INV-YYYYMM-NNNN format
    assert inv_num.startswith("INV-")
    parts = inv_num.split("-")
    assert len(parts) == 3
    assert len(parts[1]) == 6  # YYYYMM
    assert len(parts[2]) == 4  # NNNN


async def test_generate_from_time_entries(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    today = date.today()
    # Create billable time entries
    for i in range(3):
        d = today - timedelta(days=i)
        await authed_admin_client.post(
            "/api/time-entries",
            json={
                "project_id": project_id,
                "date": d.isoformat(),
                "hours": 2.0,
                "description": f"Day {i}",
                "is_billable": True,
            },
        )
    # Generate invoice from time entries
    start = (today - timedelta(days=2)).isoformat()
    end = today.isoformat()
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices/generate-from-time",
        json={"start_date": start, "end_date": end},
    )
    assert r.status_code == 201
    inv = r.json()
    assert len(inv["items"]) == 3
    assert inv["status"] == "draft"
    # Each item should be 2h * 5000 = 10000
    for item in inv["items"]:
        assert float(item["rate"]) == 5000.00


async def test_generate_from_empty_entries(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    # Use a date range with no entries
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices/generate-from-time",
        json={
            "start_date": "2020-01-01",
            "end_date": "2020-01-31",
        },
    )
    assert r.status_code == 400


async def _seed_time_entries(db_session, project_id: UUID, admin_user) -> list[TimeEntry]:
    entries = []
    for hours, is_billable in ((Decimal("1.00"), True), (Decimal("2.00"), False)):
        entry = TimeEntry(
            project_id=project_id,
            user_id=admin_user.id,
            date=date.today(),
            hours=hours,
            description=f"Seed entry {len(entries)}",
            is_billable=is_billable,
        )
        db_session.add(entry)
        entries.append(entry)
    db_session.commit()
    for entry in entries:
        db_session.refresh(entry)
    return entries


async def test_generate_excludes_nonbillable_and_marks_billed(
    authed_admin_client, db_session, admin_user
):
    project_id = await _setup_project(authed_admin_client)
    entries = await _seed_time_entries(db_session, project_id, admin_user)
    start = (date.today() - timedelta(days=1)).isoformat()
    end = (date.today() + timedelta(days=1)).isoformat()
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices/generate-from-time",
        json={"start_date": start, "end_date": end},
    )
    assert r.status_code == 201
    inv = r.json()
    billed_entry_ids = [
        UUID(item["time_entry_id"]) for item in inv["items"] if item["time_entry_id"]
    ]
    assert billed_entry_ids == [entries[0].id]
    assert float(inv["subtotal"]) == 5000.00
    assert float(inv["gst_percent"]) == 18.00
    assert float(inv["gst_amount"]) == 900.00
    assert float(inv["total"]) == 5900.00
    db_session.expire_all()
    assert db_session.get(TimeEntry, entries[0].id).is_billed is True
    assert db_session.get(TimeEntry, entries[1].id).is_billed is False


async def test_repeat_generation_rejected(authed_admin_client, db_session, admin_user):
    project_id = await _setup_project(authed_admin_client)
    entries = await _seed_time_entries(db_session, project_id, admin_user)
    start = (date.today() - timedelta(days=1)).isoformat()
    end = (date.today() + timedelta(days=1)).isoformat()
    body = {"start_date": start, "end_date": end}
    r1 = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices/generate-from-time", json=body
    )
    assert r1.status_code == 201
    r2 = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices/generate-from-time", json=body
    )
    assert r2.status_code == 400
    db_session.expire_all()
    assert db_session.get(TimeEntry, entries[0].id).is_billed is True


async def test_draft_deletion_releases_entries(authed_admin_client, db_session, admin_user):
    project_id = await _setup_project(authed_admin_client)
    entries = await _seed_time_entries(db_session, project_id, admin_user)
    start = (date.today() - timedelta(days=1)).isoformat()
    end = (date.today() + timedelta(days=1)).isoformat()
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices/generate-from-time",
        json={"start_date": start, "end_date": end},
    )
    assert r.status_code == 201
    inv_id = r.json()["id"]
    r2 = await authed_admin_client.delete(f"/api/invoices/{inv_id}")
    assert r2.status_code == 204
    db_session.expire_all()
    assert db_session.get(TimeEntry, entries[0].id).is_billed is False
    r3 = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices/generate-from-time",
        json={"start_date": start, "end_date": end},
    )
    assert r3.status_code == 201
    assert UUID(r3.json()["items"][0]["time_entry_id"]) == entries[0].id


async def test_generate_rolls_back_flags_on_failure(db_session, monkeypatch):
    today = date.today()
    project = db_session.query(Project).filter(Project.code == "TP-1").one_or_none()
    if project is None:
        client = db_session.query(Client).filter(Client.code == "TC").one_or_none()
        if client is None:
            client = Client(name="Rollback Client", code="TC", primary_email="rollback@test.com")
            db_session.add(client)
            db_session.commit()
            db_session.refresh(client)
        project = Project(client_id=client.id, name="Rollback Project", code="TP-1")
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
    entry = TimeEntry(
        project_id=project.id,
        user_id=project.client_id,
        date=today,
        hours=Decimal("1.00"),
        description="Rollback entry",
        is_billable=True,
    )
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)

    def explode(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("src.backend.services.invoice_service.create_invoice_service", explode)
    with pytest.raises(RuntimeError, match="boom"):
        generate_from_time_entries(
            db_session,
            project_id=project.id,
            user_id=project.client_id,
            start_date=today,
            end_date=today,
        )
    db_session.expire_all()
    assert db_session.get(TimeEntry, entry.id).is_billed is False
    assert db_session.query(Invoice).filter(Invoice.project_id == project.id).count() == 0


async def test_send_invoice(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    r2 = await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "sent"},
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "sent"


async def test_mark_invoice_paid(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "sent"},
    )
    r2 = await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "paid"},
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "paid"
    assert r2.json()["paid_at"] is not None


def _status_audit_rows(db_session, inv_id: str) -> list:
    """Return this invoice's status-change audit rows, newest first."""
    rows = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "invoice.status_change")
        .order_by(AuditLog.id.desc())
        .all()
    )
    return [row for row in rows if str(row.entity_id) == inv_id]


async def test_send_invoice_writes_audit_log(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    inv = r.json()
    r2 = await authed_admin_client.patch(
        f"/api/invoices/{inv['id']}/status",
        json={"status": "sent"},
    )
    assert r2.status_code == 200
    rows = _status_audit_rows(db_session, inv["id"])
    assert len(rows) == 1
    row = rows[0]
    assert row.before_json == {"status": "draft"}
    assert row.after_json["status"] == "sent"
    assert row.after_json["invoice_number"] == inv["invoice_number"]
    assert float(row.after_json["total"]) == float(inv["total"])


async def test_mark_invoice_paid_writes_audit_log(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    inv = r.json()
    await authed_admin_client.patch(
        f"/api/invoices/{inv['id']}/status",
        json={"status": "sent"},
    )
    r2 = await authed_admin_client.patch(
        f"/api/invoices/{inv['id']}/status",
        json={"status": "paid"},
    )
    assert r2.status_code == 200
    rows = _status_audit_rows(db_session, inv["id"])
    assert len(rows) == 2
    paid_row, sent_row = rows[0], rows[1]
    assert sent_row.after_json["status"] == "sent"
    assert sent_row.after_json["invoice_number"] == inv["invoice_number"]
    assert paid_row.before_json == {"status": "sent"}
    assert paid_row.after_json["status"] == "paid"
    assert paid_row.after_json["invoice_number"] == inv["invoice_number"]
    assert float(paid_row.after_json["total"]) == float(inv["total"])


async def test_cannot_delete_non_draft(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "sent"},
    )
    r2 = await authed_admin_client.delete(f"/api/invoices/{inv_id}")
    assert r2.status_code == 400


async def test_cannot_mark_paid_again(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "Item", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "sent"},
    )
    await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "paid"},
    )
    r2 = await authed_admin_client.patch(
        f"/api/invoices/{inv_id}/status",
        json={"status": "paid"},
    )
    assert r2.status_code == 400


async def test_list_invoices_by_project(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    # Create two invoices
    await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "A", "quantity": "1.00", "rate": "1000.00"},
            ],
        },
    )
    await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "B", "quantity": "2.00", "rate": "2000.00"},
            ],
        },
    )
    r = await authed_admin_client.get(f"/api/projects/{project_id}/invoices")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 2


async def test_soft_delete_invoice(authed_admin_client, db_session):
    project_id = await _setup_project(authed_admin_client)
    r = await authed_admin_client.post(
        f"/api/projects/{project_id}/invoices",
        json={
            "items": [
                {"description": "To delete", "quantity": "1.00", "rate": "500.00"},
            ],
        },
    )
    inv_id = r.json()["id"]
    r2 = await authed_admin_client.delete(f"/api/invoices/{inv_id}")
    assert r2.status_code == 204
    # Should not appear in list
    r3 = await authed_admin_client.get(f"/api/projects/{project_id}/invoices")
    ids = [i["id"] for i in r3.json()["items"]]
    assert inv_id not in ids
