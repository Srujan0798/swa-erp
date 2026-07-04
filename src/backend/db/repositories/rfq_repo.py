import uuid
from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.backend.models.rfq import RFQ, RFQItem


def get_next_rfq_number(db: Session) -> str:
    year = datetime.now(UTC).year
    prefix = f"RFQ-{year}-"
    result = (
        db.query(func.max(RFQ.rfq_number))
        .filter(RFQ.rfq_number.like(f"{prefix}%"))
        .scalar()
    )
    if result:
        try:
            seq = int(result.split("-")[-1]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f"{prefix}{seq:03d}"


def create_rfq(
    db: Session,
    *,
    project_id: uuid.UUID,
    vendor_id: uuid.UUID,
    rfq_number: str,
    created_by: uuid.UUID,
    notes: str | None = None,
    items: list[dict],
) -> RFQ:
    rfq = RFQ(
        project_id=project_id,
        vendor_id=vendor_id,
        rfq_number=rfq_number,
        created_by=created_by,
        notes=notes,
    )
    db.add(rfq)
    db.flush()

    for item_data in items:
        item = RFQItem(rfq_id=rfq.id, **item_data)
        db.add(item)

    db.commit()
    db.refresh(rfq)
    return rfq


def get_by_id(db: Session, rfq_id: uuid.UUID) -> RFQ | None:
    return (
        db.query(RFQ)
        .options(joinedload(RFQ.items))
        .filter(RFQ.id == rfq_id, RFQ.deleted_at.is_(None))
        .first()
    )


def list_by_project(
    db: Session,
    project_id: uuid.UUID,
    *,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
) -> tuple[list[RFQ], int]:
    query = db.query(RFQ).filter(
        RFQ.project_id == project_id,
        RFQ.deleted_at.is_(None),
    )
    if status:
        query = query.filter(RFQ.status == status)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(RFQ.created_at.desc()).offset(offset).limit(page_size).all()

    return items, total


def list_by_vendor(
    db: Session,
    vendor_id: uuid.UUID,
    *,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
) -> tuple[list[RFQ], int]:
    query = db.query(RFQ).filter(
        RFQ.vendor_id == vendor_id,
        RFQ.deleted_at.is_(None),
    )
    if status:
        query = query.filter(RFQ.status == status)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(RFQ.created_at.desc()).offset(offset).limit(page_size).all()

    return items, total


def update_status(
    db: Session,
    rfq_id: uuid.UUID,
    status: str,
    *,
    sent_at: datetime | None = None,
    responded_at: datetime | None = None,
    awarded_at: datetime | None = None,
) -> RFQ | None:
    rfq = db.query(RFQ).filter(RFQ.id == rfq_id, RFQ.deleted_at.is_(None)).first()
    if not rfq:
        return None
    rfq.status = status
    if sent_at is not None:
        rfq.sent_at = sent_at
    if responded_at is not None:
        rfq.responded_at = responded_at
    if awarded_at is not None:
        rfq.awarded_at = awarded_at
    db.commit()
    db.refresh(rfq)
    return rfq


def update_item_rates(
    db: Session,
    rfq_id: uuid.UUID,
    items_data: list[dict],
) -> None:
    for item_data in items_data:
        item = (
            db.query(RFQItem)
            .filter(
                RFQItem.rfq_id == rfq_id,
                RFQItem.id == item_data["item_id"],
            )
            .first()
        )
        if item:
            item.vendor_rate = item_data["vendor_rate"]
    db.commit()


def compare_vendors(
    db: Session,
    project_id: uuid.UUID,
    material_ids: list[uuid.UUID] | None = None,
) -> list[dict]:
    from src.backend.models.vendor import Vendor

    query = (
        db.query(RFQ, RFQItem, Vendor.name)
        .join(RFQItem, RFQItem.rfq_id == RFQ.id)
        .join(Vendor, Vendor.id == RFQ.vendor_id)
        .filter(
            RFQ.project_id == project_id,
            RFQ.deleted_at.is_(None),
        )
    )
    if material_ids:
        query = query.filter(RFQItem.material_id.in_(material_ids))

    results = query.all()

    material_map: dict[uuid.UUID, dict] = {}
    for rfq, item, vendor_name in results:
        mat_id = item.material_id
        if mat_id not in material_map:
            material_map[mat_id] = {"material_id": mat_id, "vendors": []}
        material_map[mat_id]["vendors"].append({
            "vendor_id": rfq.vendor_id,
            "vendor_name": vendor_name,
            "rfq_id": rfq.id,
            "rfq_number": rfq.rfq_number,
            "rate": item.vendor_rate,
        })

    return list(material_map.values())


def soft_delete(db: Session, rfq_id: uuid.UUID) -> bool:
    rfq = db.query(RFQ).filter(RFQ.id == rfq_id, RFQ.deleted_at.is_(None)).first()
    if not rfq:
        return False
    rfq.deleted_at = datetime.now(UTC)
    db.commit()
    return True
