import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.backend.db.repositories import audit_repo, token_repo
from src.backend.models.token import Token
from src.backend.schemas.token import TokenCreate, TokenUpdate
from src.backend.services.reference_id_service import generate_reference_id


def list_tokens_service(
    db: Session,
    page: int,
    page_size: int,
    agreement_id: uuid.UUID | None,
    project_id: uuid.UUID | None,
    token_status: str | None,
    q: str | None,
) -> tuple[list[Token], int, int, int]:
    items, total = token_repo.list_tokens(
        db,
        page=page,
        page_size=page_size,
        agreement_id=agreement_id,
        project_id=project_id,
        token_status=token_status,
        q=q,
    )
    return items, total, page, page_size


def get_token_service(db: Session, token_id: uuid.UUID) -> Token | None:
    return token_repo.get_by_id(db, token_id)


def create_token_service(
    db: Session,
    data: TokenCreate,
    actor_id: uuid.UUID,
) -> Token:
    reference_id = generate_reference_id(db, "TKN")
    payload: dict[str, Any] = data.model_dump()
    payload["reference_id"] = reference_id
    payload["token_status"] = data.token_status or "In Progress"
    payload["tokens_used"] = data.tokens_used if data.tokens_used is not None else 1
    token = token_repo.create(db, payload)
    audit_repo.create_entry(
        db,
        action="token.create",
        entity_type="token",
        entity_id=token.id,
        user_id=actor_id,
        after_json={
            "id": str(token.id),
            "reference_id": token.reference_id,
            "agreement_id": str(token.agreement_id),
            "token_date": str(token.token_date),
            "token_status": token.token_status,
        },
    )
    return token


def update_token_service(
    db: Session,
    token_id: uuid.UUID,
    data: TokenUpdate,
    actor_id: uuid.UUID,
) -> Token | None:
    token = token_repo.get_by_id(db, token_id)
    if not token:
        return None
    before = {
        "token_status": token.token_status,
        "tokens_used": token.tokens_used,
        "description": token.description,
    }
    update_data = data.model_dump(exclude_unset=True)
    token_repo.update(db, token, update_data)
    audit_repo.create_entry(
        db,
        action="token.update",
        entity_type="token",
        entity_id=token_id,
        user_id=actor_id,
        before_json=before,
        after_json={
            "token_status": token.token_status,
            "tokens_used": token.tokens_used,
            "description": token.description,
        },
    )
    return token


def soft_delete_token_service(
    db: Session,
    token_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> bool:
    token = token_repo.get_by_id(db, token_id)
    if not token:
        return False
    token_repo.soft_delete(db, token)
    audit_repo.create_entry(
        db,
        action="token.delete",
        entity_type="token",
        entity_id=token_id,
        user_id=actor_id,
        after_json={"deleted_at": str(token.deleted_at)},
    )
    return True
