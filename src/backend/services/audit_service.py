from typing import Any

from sqlalchemy.orm import Session

from src.backend.db.repositories.audit_repo import create_entry


def record_event(
    db: Session,
    action: str,
    entity_type: str = "auth",
    user_id: Any = None,
    entity_id: Any = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    create_entry(
        db=db,
        action=action,
        entity_type=entity_type,
        user_id=user_id,
        entity_id=entity_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
