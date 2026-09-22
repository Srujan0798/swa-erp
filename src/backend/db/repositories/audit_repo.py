import ipaddress
import json
import uuid as _uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.backend.models.audit_log import AuditLog


class _SafeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, _uuid.UUID):
            return str(o)
        if isinstance(o, datetime | date):
            return o.isoformat()
        return super().default(o)


def _make_json_safe(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is None:
        return None
    return json.loads(json.dumps(data, cls=_SafeEncoder))


def _sanitize_ip(value: str | None) -> str | None:
    """Coerce to a valid IP or None.

    The column is INET; request hosts can be names ("testclient", proxy
    hostnames). Audit must never crash the operation it records.
    """
    if not value:
        return None
    try:
        return str(ipaddress.ip_address(value.strip().split("%")[0]))
    except ValueError:
        return None


def create_entry(
    db: Session,
    action: str,
    entity_type: str,
    user_id: _uuid.UUID | None = None,
    entity_id: _uuid.UUID | None = None,
    before_json: dict[str, Any] | None = None,
    after_json: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_json=_make_json_safe(before_json),
        after_json=_make_json_safe(after_json),
        ip_address=_sanitize_ip(ip_address),
        user_agent=user_agent,
    )
    db.add(entry)
    db.flush()
    db.refresh(entry)
    return entry
