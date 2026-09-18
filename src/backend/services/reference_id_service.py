import uuid
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.backend.models.reference_counter import ReferenceCounter


def _utc_year() -> int:
    return datetime.now(UTC).year


def generate_reference_id(db: Session, entity_type: str) -> str:
    year = _utc_year()
    sql = text(
        """
        INSERT INTO reference_counters (id, entity_type, year, last_seq)
        VALUES (:id, :entity_type, :year, 1)
        ON CONFLICT (entity_type, year) DO UPDATE
        SET last_seq = reference_counters.last_seq + 1
        RETURNING last_seq
    """
    )
    # Use a separate autocommit connection so the counter persists
    # even if the caller's transaction rolls back (e.g., in tests).
    from sqlalchemy.engine import Engine

    bind = db.get_bind()
    engine = bind.engine if hasattr(bind, "engine") else bind
    if not isinstance(engine, Engine):
        raise RuntimeError("Expected SQLAlchemy Engine for reference ID generation")
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        result = conn.execute(sql, {"id": uuid.uuid4(), "entity_type": entity_type, "year": year})
        row = result.fetchone()
    if row is None:
        raise RuntimeError("Failed to generate reference ID")
    seq = row[0]
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
