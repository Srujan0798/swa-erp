import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.backend.models.reference_counter import ReferenceCounter


def _utc_year() -> int:
    return datetime.now(UTC).year


def generate_reference_id(db: Session, entity_type: str) -> str:
    year = _utc_year()
    # Lock the counter row first so concurrent callers serialize on the same
    # (entity_type, year) row. In READ COMMITTED, SELECT FOR UPDATE blocks
    # concurrent readers until the current txn commits/aborts, giving each
    # caller a monotonic seq.
    row = (
        db.query(ReferenceCounter)
        .filter(ReferenceCounter.entity_type == entity_type, ReferenceCounter.year == year)
        .with_for_update()
        .one_or_none()
    )
    if row is not None:
        row.last_seq += 1
        seq = row.last_seq
    else:
        # First caller for this (entity_type, year): insert at seq=1.
        # Use ON CONFLICT as a safety net in case a concurrent txn inserted
        # the row between our SELECT FOR UPDATE and this INSERT (shouldn't
        # happen under FOR UPDATE, but defend anyway).
        try:
            new_row = ReferenceCounter(
                id=uuid.uuid4(),
                entity_type=entity_type,
                year=year,
                last_seq=1,
            )
            db.add(new_row)
            db.flush()
            seq = 1
        except IntegrityError:
            db.rollback()
            # Concurrent txn won the race — re-read and bump.
            row = (
                db.query(ReferenceCounter)
                .filter(ReferenceCounter.entity_type == entity_type, ReferenceCounter.year == year)
                .with_for_update()
                .one()
            )
            row.last_seq += 1
            seq = row.last_seq

    return f"SWA-{year}-{entity_type}-{seq:03d}"


def get_current_seq(db: Session, entity_type: str, year: int | None = None) -> int:
    if year is None:
        year = _utc_year()
    row = (
        db.query(ReferenceCounter)
        .filter(ReferenceCounter.entity_type == entity_type, ReferenceCounter.year == year)
        .one_or_none()
    )
    return row.last_seq if row else 0
