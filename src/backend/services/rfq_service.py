import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.backend.core.rfq_workflow import can_transition
from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.rfq_repo import (
    compare_vendors,
    create_rfq,
    get_by_id,
    get_next_rfq_number,
    list_by_project,
    list_by_vendor,
    soft_delete,
    update_item_rates,
    update_status,
)
from src.backend.schemas.rfq import (
    RFQCompareMaterial,
    RFQCompareVendor,
    RFQListResponse,
    RFQListItem,
    RFQRead,
    RFQResponseItem,
)


def _enforce_transition(rfq, to_status: str) -> None:
    if not can_transition(rfq.status, to_status):
        msg = f"Cannot transition from {rfq.status} to {to_status}"
        raise ValueError(msg)


def _to_read(rfq) -> RFQRead:
    from src.backend.models.material import Material
    from src.backend.models.user import User
    from src.backend.models.vendor import Vendor

    items = []
    for item in rfq.items:
        material = item._sa_instance_state.manager.class_
        items.append({
            "id": item.id,
            "rfq_id": item.rfq_id,
            "material_id": item.material_id,
            "material_name": getattr(item, "_material_name", None),
            "material_unit": getattr(item, "_material_unit", None),
            "quantity": item.quantity,
            "vendor_rate": item.vendor_rate,
            "notes": item.notes,
        })

    return RFQRead(
        id=rfq.id,
        project_id=rfq.project_id,
        project_name=getattr(rfq, "_project_name", None),
        vendor_id=rfq.vendor_id,
        vendor_name=getattr(rfq, "_vendor_name", None),
        status=rfq.status,
        rfq_number=rfq.rfq_number,
        created_by=rfq.created_by,
        created_by_name=getattr(rfq, "_creator_name", None),
        sent_at=rfq.sent_at,
        responded_at=rfq.responded_at,
        awarded_at=rfq.awarded_at,
        notes=rfq.notes,
        created_at=rfq.created_at,
        items=items,
    )


def create_rfq_with_items(
    db: Session,
    *,
    project_id: uuid.UUID,
    vendor_id: uuid.UUID,
    notes: str | None,
    items_data: list[dict],
    created_by: uuid.UUID,
) -> RFQRead:
    rfq_number = get_next_rfq_number(db)
    rfq = create_rfq(
        db,
        project_id=project_id,
        vendor_id=vendor_id,
        rfq_number=rfq_number,
        created_by=created_by,
        notes=notes,
        items=items_data,
    )

    create_entry(
        db,
        action="rfq.create",
        entity_type="rfq",
        entity_id=rfq.id,
        user_id=created_by,
        after_json={
            "project_id": str(project_id),
            "vendor_id": str(vendor_id),
            "rfq_number": rfq_number,
            "item_count": len(items_data),
        },
    )

    return get_rfq(db, rfq.id)


def send_rfq(db: Session, rfq_id: uuid.UUID, sent_by: uuid.UUID) -> RFQRead:
    rfq = get_by_id(db, rfq_id)
    if not rfq:
        msg = "RFQ not found"
        raise ValueError(msg)
    _enforce_transition(rfq, "sent")

    before_json = {"status": rfq.status}
    update_status(db, rfq_id, "sent", sent_at=datetime.now(timezone.utc))

    create_entry(
        db,
        action="rfq.send",
        entity_type="rfq",
        entity_id=rfq_id,
        user_id=sent_by,
        before_json=before_json,
        after_json={"status": "sent"},
    )

    return get_rfq(db, rfq_id)


def receive_response(
    db: Session,
    rfq_id: uuid.UUID,
    items_data: list[dict],
    responded_by: uuid.UUID,
) -> RFQRead:
    rfq = get_by_id(db, rfq_id)
    if not rfq:
        msg = "RFQ not found"
        raise ValueError(msg)
    _enforce_transition(rfq, "responded")

    before_json = {"status": rfq.status}
    update_status(
        db, rfq_id, "responded", responded_at=datetime.now(timezone.utc)
    )
    update_item_rates(db, rfq_id, items_data)

    create_entry(
        db,
        action="rfq.respond",
        entity_type="rfq",
        entity_id=rfq_id,
        user_id=responded_by,
        before_json=before_json,
        after_json={"status": "responded", "item_count": len(items_data)},
    )

    return get_rfq(db, rfq_id)


def compare_rfq(
    db: Session,
    project_id: uuid.UUID,
    material_ids: list[uuid.UUID] | None = None,
) -> list[RFQCompareMaterial]:
    raw = compare_vendors(db, project_id, material_ids)
    result = []
    for mat in raw:
        vendors = [
            RFQCompareVendor(
                vendor_id=v["vendor_id"],
                vendor_name=v["vendor_name"],
                rfq_id=v["rfq_id"],
                rfq_number=v["rfq_number"],
                rate=v["rate"],
            )
            for v in mat["vendors"]
        ]
        result.append(
            RFQCompareMaterial(
                material_id=mat["material_id"],
                vendors=vendors,
            )
        )
    return result


def award_rfq(db: Session, rfq_id: uuid.UUID, awarded_by: uuid.UUID) -> RFQRead:
    rfq = get_by_id(db, rfq_id)
    if not rfq:
        msg = "RFQ not found"
        raise ValueError(msg)
    _enforce_transition(rfq, "awarded")

    before_json = {"status": rfq.status}
    update_status(db, rfq_id, "awarded", awarded_at=datetime.now(timezone.utc))

    create_entry(
        db,
        action="rfq.award",
        entity_type="rfq",
        entity_id=rfq_id,
        user_id=awarded_by,
        before_json=before_json,
        after_json={"status": "awarded"},
    )

    return get_rfq(db, rfq_id)


def close_rfq(db: Session, rfq_id: uuid.UUID, closed_by: uuid.UUID) -> RFQRead:
    rfq = get_by_id(db, rfq_id)
    if not rfq:
        msg = "RFQ not found"
        raise ValueError(msg)
    _enforce_transition(rfq, "closed")

    before_json = {"status": rfq.status}
    update_status(db, rfq_id, "closed")

    create_entry(
        db,
        action="rfq.close",
        entity_type="rfq",
        entity_id=rfq_id,
        user_id=closed_by,
        before_json=before_json,
        after_json={"status": "closed"},
    )

    return get_rfq(db, rfq_id)


def cancel_rfq(db: Session, rfq_id: uuid.UUID, cancelled_by: uuid.UUID) -> RFQRead:
    rfq = get_by_id(db, rfq_id)
    if not rfq:
        msg = "RFQ not found"
        raise ValueError(msg)
    _enforce_transition(rfq, "cancelled")

    before_json = {"status": rfq.status}
    update_status(db, rfq_id, "cancelled")

    create_entry(
        db,
        action="rfq.cancel",
        entity_type="rfq",
        entity_id=rfq_id,
        user_id=cancelled_by,
        before_json=before_json,
        after_json={"status": "cancelled"},
    )

    return get_rfq(db, rfq_id)


def get_rfq(db: Session, rfq_id: uuid.UUID) -> RFQRead | None:
    rfq = get_by_id(db, rfq_id)
    if not rfq:
        return None

    from src.backend.models.material import Material
    from src.backend.models.user import User
    from src.backend.models.vendor import Vendor

    vendor = db.query(Vendor).filter(Vendor.id == rfq.vendor_id).first()
    creator = db.query(User).filter(User.id == rfq.created_by).first()
    rfq._vendor_name = vendor.name if vendor else None
    rfq._creator_name = creator.name if creator else None

    for item in rfq.items:
        material = db.query(Material).filter(Material.id == item.material_id).first()
        item._material_name = material.name if material else None
        item._material_unit = material.unit if material else None

    return _to_read(rfq)


def list_project_rfqs(
    db: Session,
    project_id: uuid.UUID,
    *,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
) -> RFQListResponse:
    items, total = list_by_project(db, project_id, page=page, page_size=page_size, status=status)

    from src.backend.models.vendor import Vendor

    reads = []
    for rfq in items:
        vendor = db.query(Vendor).filter(Vendor.id == rfq.vendor_id).first()
        reads.append(
            RFQListItem(
                id=rfq.id,
                project_id=rfq.project_id,
                vendor_id=rfq.vendor_id,
                vendor_name=vendor.name if vendor else None,
                status=rfq.status,
                rfq_number=rfq.rfq_number,
                created_by=rfq.created_by,
                sent_at=rfq.sent_at,
                responded_at=rfq.responded_at,
                awarded_at=rfq.awarded_at,
                notes=rfq.notes,
                created_at=rfq.created_at,
                item_count=len(rfq.items) if rfq.items else 0,
            )
        )

    return RFQListResponse(items=reads, total=total, page=page, page_size=page_size)
