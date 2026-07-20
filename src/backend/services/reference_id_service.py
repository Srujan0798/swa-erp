import uuid
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.backend.models.reference_counter import ReferenceCounter


def _utc_year() -> int:
    return datetime.now(UTC).year


def generate_reference_id(db: Session, entity_type: str) -> str:
    year = _utc_year()
    new_id = uuid.uuid4()
    stmt = text(
        """
        INSERT INTO reference_counters (id, entity_type, year, last_seq)
        VALUES (:new_id, :entity_type, :year, 1)
        ON CONFLICT (entity_type, year)
        DO UPDATE SET last_seq = reference_counters.last_seq + 1
        RETURNING last_seq
        """
    )
    result = db.execute(
        stmt, {"new_id": new_id, "entity_type": entity_type, "year": year}
    ).scalar_one()
    db.commit()
    return f"SWA-{year}-{entity_type}-{result:03d}"


def get_current_seq(db: Session, entity_type: str, year: int | None = None) -> int:
    if year is None:
        year = _utc_year()
    row = (
        db.query(ReferenceCounter)
        .filter(ReferenceCounter.entity_type == entity_type, ReferenceCounter.year == year)
        .one_or_none()
    )
    return row.last_seq if row else 0
