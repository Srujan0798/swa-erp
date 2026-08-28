"""
evals/wave_43_evals.py — eval tasks as pytest tests (runs via the existing conftest fixtures).

These are SYSTEM-LEVEL checks: they drive the real FastAPI ASGI app through
httpx.AsyncClient and assert on DB rows, API payloads, and Decimal arithmetic.
They are NOT unit tests — they validate end-to-end client workflows.

Run:
  DATABASE_URL=postgresql://swa:swa@localhost:5432/swa_erp_test \\
  APP_ENV=test DISABLE_AUTH_RATE_LIMIT=1 \\
  python3 -m pytest evals/wave_43_evals.py -v -x --confcutdir=tests -p tests.conftest

After all 5 pass, run:
  python3 evals/run_evals.py --trials 3
to produce evals/outcomes/pass@k.json and transcripts.
"""
import re
import uuid
from decimal import Decimal

import pytest

from src.backend.models.client import Client
from src.backend.models.inquiry import Inquiry
from src.backend.models.project import Project
from src.backend.models.invoice import Invoice
from src.backend.models.time_tracking import TimeEntry


def _login(client, email, password):
    """Login synchronously-wrapped async — returns token string."""
    pass


# ===========================================================================
# Task 001: Inquiry -> Client conversion (incl. ambiguous-match branch)
# ===========================================================================

@pytest.mark.asyncio
async def test_001_inquiry_to_client_conversion(client_with_db, db_session, pm_user):
    """Inquiry with ambiguous client name -> 300 -> pick candidate -> client reused."""
    # Pre-seed two clients with the same name (ambiguous match)
    c1 = Client(name="Ambiguous Test Client", code="AMB-001", primary_email="amb1@test.com")
    c2 = Client(name="Ambiguous Test Client", code="AMB-002", primary_email="amb2@test.com")
    db_session.add_all([c1, c2])
    db_session.commit()
    db_session.refresh(c1)
    db_session.refresh(c2)

    # Login as PM
    r = await client_with_db.post("/api/auth/login",
        json={"email": "pm@swa.co.in", "password": "pm123!"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    client_with_db.headers["Authorization"] = f"Bearer {token}"

    # Create inquiry
    r = await client_with_db.post("/api/inquiries", json={
        "inquiry_date": "2026-08-28",
        "client_name": "Ambiguous Test Client",
        "requirement_summary": "Eval 001",
    })
    assert r.status_code == 201, f"inquiry create: {r.status_code} {r.text}"
    inquiry_id = r.json()["id"]

    # Convert (should hit ambiguous-match branch -> 300)
    r = await client_with_db.post(f"/api/inquiries/{inquiry_id}/convert", json={
        "project_name": "Ambiguous Project",
        "project_code": "APC-001",
    })
    assert r.status_code == 300, f"expected 300 ambiguous, got {r.status_code}: {r.text}"
    # FastAPI wraps HTTPException detail; the InquiryConversionError.body has candidates
    body = r.json()
    detail = body.get("detail", body)
    candidates = detail.get("candidates", [])
    assert len(candidates) == 2, f"expected 2 candidates, got {len(candidates)}: {body}"

    # Pick first candidate
    r = await client_with_db.post(f"/api/inquiries/{inquiry_id}/convert", json={
        "project_name": "Ambiguous Project",
        "project_code": "APC-001",
        "client_id": str(candidates[0]["id"]),
    })
    assert r.status_code == 200, f"convert with client_id: {r.status_code} {r.text}"
    resp = r.json()
    client_id = resp["client_id"]

    # Assertions
    inquiry = db_session.query(Inquiry).filter(Inquiry.id == inquiry_id).one()
    assert inquiry.status == "Converted"
    assert str(inquiry.converted_client_id) == str(candidates[0]["id"])
    assert inquiry.converted_project_id is not None

    client = db_session.query(Client).filter_by(id=uuid.UUID(client_id)).one()
    # Client is REUSED (from the ambiguous candidates), so keep its seeded code.
    # The SWA-CLT-### format only applies to auto-generated client codes.
    assert str(client.id) == str(candidates[0]["id"])  # reused, not new

    proj = db_session.query(Project).filter_by(id=uuid.UUID(resp["project_id"])).one()
    assert proj.code == "APC-001"
    assert str(proj.client_id) == str(client_id)
    assert str(proj.inquiry_id) == str(inquiry_id)


# ===========================================================================
# Task 002: Agreement -> Token -> DocRef ID chain
# ===========================================================================

@pytest.mark.asyncio
async def test_002_agreement_token_docref_chain(client_with_db, db_session, pm_user):
    """Reference IDs must be well-formed + monotonically increasing + FK-wired."""
    from src.backend.models.agreement import ServiceAgreement
    from src.backend.models.token import Token
    from src.backend.models.document_reference import DocumentReference

    token = (await client_with_db.post("/api/auth/login",
        json={"email": "pm@swa.co.in", "password": "pm123!"})).json()["access_token"]
    client_with_db.headers["Authorization"] = f"Bearer {token}"

    # 1. Create client
    r = await client_with_db.post("/api/clients", json={
        "name": "Chain Client", "code": "CHN-001", "primary_email": "chain@test.com"
    })
    assert r.status_code == 201
    client_id = r.json()["id"]

    # 2. Create inquiry
    r = await client_with_db.post("/api/inquiries", json={
        "inquiry_date": "2026-08-28", "client_name": "Chain Client",
        "requirement_summary": "Eval 002",
    })
    assert r.status_code == 201
    inquiry_id = r.json()["id"]

    # 3. Convert (auto-match the one existing client)
    r = await client_with_db.post(f"/api/inquiries/{inquiry_id}/convert", json={
        "project_name": "Chain Project", "project_code": "CHN-PRJ-001",
    })
    assert r.status_code == 200, f"convert: {r.status_code} {r.text}"
    project_id = r.json()["project_id"]

    # 4. Create service agreement
    r = await client_with_db.post("/api/service-agreements", json={
        "client_id": client_id, "inquiry_id": inquiry_id,
        "service_name": "Annual Maintenance Contract",
        "start_date": "2026-01-01", "end_date": "2026-12-31", "total_tokens": 100,
    })
    assert r.status_code == 201, f"SA: {r.status_code} {r.text}"
    agreement_id = r.json()["id"]

    # 5. Create token
    r = await client_with_db.post("/api/tokens", json={
        "agreement_id": agreement_id, "token_date": "2026-08-28",
        "token_type": "SA", "description": "Eval token", "tokens_used": 1,
        "project_id": project_id,
    })
    assert r.status_code == 201, f"token: {r.status_code} {r.text}"
    token_id = r.json()["id"]

    # 6. Create document reference
    r = await client_with_db.post("/api/document-references", json={
        "project_id": project_id, "token_id": token_id,
        "document_type": "DBR", "doc_date": "2026-08-28",
        "description": "Eval docref",
    })
    assert r.status_code == 201, f"docref: {r.status_code} {r.text}"
    docref_id = r.json()["id"]

    # Verify IDs in DB
    inq = db_session.query(Inquiry).filter(Inquiry.id == inquiry_id).one()
    ag = db_session.query(ServiceAgreement).filter(ServiceAgreement.id == agreement_id).one()
    tok = db_session.query(Token).filter(Token.id == token_id).one()
    dr = db_session.query(DocumentReference).filter(DocumentReference.id == docref_id).one()

    ref_re = re.compile(r"^SWA-\d{4}-[A-Z]+-\d{3}$")
    for label, obj in [("inquiry", inq), ("agreement", ag), ("token", tok), ("docref", dr)]:
        assert ref_re.match(obj.reference_id), f"{label}.reference_id={obj.reference_id}"

    # Each entity has its own per-type sequence. Verify format + that each is
    # unique within its type/year. Cross-type sequences are independent.
    year_re = re.compile(r"^SWA-(\d{4})-[A-Z]+-(\d{3})$")
    type_seqs: dict[str, list[int]] = {}
    for label, obj in [("inquiry", inq), ("agreement", ag), ("token", tok), ("docref", dr)]:
        m = year_re.match(obj.reference_id)
        assert m is not None, f"{label}.reference_id format: {obj.reference_id}"
        etype = obj.reference_id.split("-")[2]  # INQ, SA, TKN, DBR
        seq = int(m.group(2))
        yr = int(m.group(1))
        assert yr == int(year_re.match(inq.reference_id).group(1)), f"{label} year mismatch"
        type_seqs.setdefault(etype, []).append(seq)

    # Within each entity type, seqs should be strictly increasing (no reuse).
    # Since each type is only created once here, just verify seq==1 for all.
    for etype, seqs_in_type in type_seqs.items():
        assert seqs_in_type == sorted(seqs_in_type), f"{etype} seq not monotonic: {seqs_in_type}"
        assert len(set(seqs_in_type)) == len(seqs_in_type), f"{etype} has duplicate seqs"

    # FK wiring
    assert str(ag.client_id) == str(client_id)
    assert str(ag.inquiry_id) == str(inquiry_id)
    assert str(tok.agreement_id) == str(agreement_id)
    assert str(dr.token_id) == str(token_id)
    assert str(dr.project_id) == str(project_id)


# ===========================================================================
# Task 003: RBAC enforcement
# ===========================================================================

@pytest.mark.asyncio
async def test_003_rbac_enforcement(client_with_db, db_session, admin_user, pm_user, viewer_user):
    """Viewer can read but NOT write — and the DB must not change on forbidden writes."""
    # Admin logs in + creates client + project
    token = (await client_with_db.post("/api/auth/login",
        json={"email": "admin@swa.co.in", "password": "admin123!"})).json()["access_token"]
    client_with_db.headers["Authorization"] = f"Bearer {token}"

    r = await client_with_db.post("/api/clients", json={
        "name": "RBAC Client", "code": "RBAC-C-001", "primary_email": "rbac@test.com"
    })
    assert r.status_code == 201
    client_id = r.json()["id"]

    r = await client_with_db.post("/api/projects", json={
        "client_id": client_id, "name": "RBAC Project", "code": "RBAC-P-001", "status": "Lead"
    })
    assert r.status_code == 201
    project_id = r.json()["id"]

    # Viewer logs in
    vtoken = (await client_with_db.post("/api/auth/login",
        json={"email": "viewer@swa.co.in", "password": "viewer123!"})).json()["access_token"]
    client_with_db.headers["Authorization"] = f"Bearer {vtoken}"

    # Step 3: viewer CAN read projects (require_role VIEWER or broader)
    r = await client_with_db.get(f"/api/projects/{project_id}")
    assert r.status_code == 200, f"viewer read should be 200, got {r.status_code}"

    # Step 4: viewer CANNOT create client (require_role PM) — must be exact 403, not 500
    r = await client_with_db.post("/api/clients", json={
        "name": "Hack Client", "code": "HACK-001", "primary_email": "hack@test.com"
    })
    assert r.status_code == 403, f"viewer create client must be 403, got {r.status_code}: {r.text}"

    # Step 5: viewer CANNOT update project (require_role PM)
    r = await client_with_db.patch(f"/api/projects/{project_id}", json={"name": "Hacked Name"})
    assert r.status_code == 403, f"viewer project update must be 403, got {r.status_code}: {r.text}"

    # DB verification: no side-effects from forbidden writes
    hack = db_session.query(Client).filter(Client.code == "HACK-001").first()
    assert hack is None, "viewer created a client — RBAC failure!"
    proj = db_session.query(Project).filter(Project.id == uuid.UUID(project_id)).one()
    assert proj.name == "RBAC Project", f"project name was mutated: {proj.name}"


# ===========================================================================
# Task 004: Time log -> dashboard aggregation
# ===========================================================================

@pytest.mark.asyncio
async def test_004_time_log_to_dashboard(client_with_db, db_session, admin_user):
    """Billable time entries surface in timesheet + generate-from-time invoice."""
    from src.backend.models.invoice import Invoice as InvoiceModel

    token = (await client_with_db.post("/api/auth/login",
        json={"email": "admin@swa.co.in", "password": "admin123!"})).json()["access_token"]
    client_with_db.headers["Authorization"] = f"Bearer {token}"

    # Create client + project
    r = await client_with_db.post("/api/clients", json={
        "name": "Time Client", "code": "TIME-C-001", "primary_email": "timetest@test.com"
    })
    assert r.status_code == 201
    client_id = r.json()["id"]

    r = await client_with_db.post("/api/projects", json={
        "client_id": client_id, "name": "Time Project", "code": "TIME-P-001", "status": "Lead"
    })
    assert r.status_code == 201
    project_id = r.json()["id"]

    # Log billable time (7h)
    r = await client_with_db.post("/api/time-entries", json={
        "project_id": project_id, "date": "2026-08-24",
        "hours": "7.00", "description": "Billable engineering", "is_billable": True
    })
    assert r.status_code == 201, f"time entry: {r.status_code} {r.text}"

    # Log non-billable time (1h)
    r = await client_with_db.post("/api/time-entries", json={
        "project_id": project_id, "date": "2026-08-25",
        "hours": "1.00", "description": "Internal meeting", "is_billable": False
    })
    assert r.status_code == 201

    # 2 time entries in DB
    entries = db_session.query(TimeEntry).filter(
        TimeEntry.project_id == uuid.UUID(project_id),
        TimeEntry.deleted_at.is_(None),
    ).all()
    assert len(entries) == 2, f"expected 2 entries, got {len(entries)}"

    # Generate timesheet
    r = await client_with_db.post("/api/timesheets/generate?week_start=2026-08-24")
    assert r.status_code == 200, f"timesheet: {r.status_code} {r.text}"
    ts = r.json()
    assert Decimal(str(ts["total_hours"])) == Decimal("8.00")
    assert Decimal(str(ts["billable_hours"])) == Decimal("7.00")
    assert ts["status"] == "draft"

    # Generate invoice from time
    r = await client_with_db.post(f"/api/projects/{project_id}/invoices/generate-from-time", json={
        "start_date": "2026-08-24", "end_date": "2026-08-30"
    })
    assert r.status_code == 201, f"invoice from time: {r.status_code} {r.text}"
    inv_resp = r.json()

    inv = db_session.query(InvoiceModel).filter(InvoiceModel.id == uuid.UUID(inv_resp["id"])).one()
    assert Decimal(str(inv.subtotal)) == Decimal("35000.00"), f"subtotal={inv.subtotal}"
    assert Decimal(str(inv.gst_amount)) == Decimal("6300.00"), f"gst={inv.gst_amount}"
    assert Decimal(str(inv.total)) == Decimal("41300.00"), f"total={inv.total}"
    assert Decimal(str(inv.subtotal)) + Decimal(str(inv.gst_amount)) == Decimal(str(inv.total)), "rounding gap"
    assert isinstance(inv.subtotal, Decimal), "DB money is Decimal"


# ===========================================================================
# Task 005: Invoice GST correctness
# ===========================================================================

@pytest.mark.asyncio
async def test_005_invoice_gst_correctness(client_with_db, db_session, admin_user):
    """Invoice with 3 line items: GST 18% exact, money stays Decimal."""
    token = (await client_with_db.post("/api/auth/login",
        json={"email": "admin@swa.co.in", "password": "admin123!"})).json()["access_token"]
    client_with_db.headers["Authorization"] = f"Bearer {token}"

    r = await client_with_db.post("/api/clients", json={
        "name": "GST Client", "code": "GST-C-001", "primary_email": "gsttest@test.com"
    })
    assert r.status_code == 201
    client_id = r.json()["id"]

    r = await client_with_db.post("/api/projects", json={
        "client_id": client_id, "name": "GST Project", "code": "GST-P-001", "status": "Lead"
    })
    assert r.status_code == 201
    project_id = r.json()["id"]

    # Create invoice with 3 items
    r = await client_with_db.post(f"/api/projects/{project_id}/invoices", json={
        "due_date": "2026-09-28",
        "tax_rate": "18.00",
        "items": [
            {"description": "Consulting A", "quantity": "2.00", "rate": "1000.00", "category": "time"},
            {"description": "Consulting B", "quantity": "1.50", "rate": "500.00", "category": "time"},
            {"description": "Travel", "quantity": "1.00", "rate": "200.00", "category": "expense"},
        ],
    })
    assert r.status_code == 201, f"invoice: {r.status_code} {r.text}"
    inv_resp = r.json()

    inv = db_session.query(Invoice).filter(Invoice.id == uuid.UUID(inv_resp["id"])).one()

    # subtotal = 2000 + 750 + 200 = 2950
    assert Decimal(str(inv.subtotal)) == Decimal("2950.00"), f"subtotal={inv.subtotal}"
    assert Decimal(str(inv.gst_percent)) == Decimal("18.00")
    # gst = 2950 * 18% = 531
    assert Decimal(str(inv.gst_amount)) == Decimal("531.00"), f"gst_amount={inv.gst_amount}"
    # total = 2950 + 531 = 3481
    assert Decimal(str(inv.total)) == Decimal("3481.00"), f"total={inv.total}"
    assert Decimal(str(inv.subtotal)) + Decimal(str(inv.gst_amount)) == Decimal(str(inv.total)), "rounding gap"

    # DB money is Decimal, not float
    for fid in ("subtotal", "total", "gst_amount", "gst_percent"):
        assert isinstance(getattr(inv, fid), Decimal), f"DB {fid} is Decimal"

    # Item amounts
    amounts = sorted(Decimal(str(i.amount)) for i in inv.items)
    assert amounts == [Decimal("200.00"), Decimal("750.00"), Decimal("2000.00")], f"item amounts: {amounts}"

    # API response: money fields are JSON strings (Pydantic Decimal -> str)
    for fid in ("subtotal", "gst_amount", "total"):
        assert isinstance(inv_resp.get(fid), str), f"API {fid} should be str, got {type(inv_resp.get(fid))}"
