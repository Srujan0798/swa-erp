import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.backend.models.token import Token


def list_tokens(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    agreement_id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
    token_status: str | None = None,
    q: str | None = None,
) -> tuple[list[Token], int]:
    query = db.query(Token).filter(Token.deleted_at.is_(None))
    if agreement_id is not None:
        query = query.filter(Token.agreement_id == agreement_id)
    if project_id is not None:
        query = query.filter(Token.project_id == project_id)
    if token_status:
        query = query.filter(Token.token_status == token_status)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Token.reference_id.ilike(like),
                Token.description.ilike(like),
                Token.client_employee_name.ilike(like),
            )
        )
    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Token.created_at.desc()).offset(offset).limit(page_size).all()
    return list(items), total


def get_by_id(db: Session, token_id: uuid.UUID) -> Token | None:
    return (
        db.query(Token)
        .filter(Token.id == token_id, Token.deleted_at.is_(None))
        .first()
    )


def get_by_reference_id(db: Session, reference_id: str) -> Token | None:
    return (
        db.query(Token)
        .filter(Token.reference_id == reference_id, Token.deleted_at.is_(None))
        .first()
    )


def create(db: Session, data: dict[str, Any]) -> Token:
    token = Token(**data)
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def update(db: Session, token: Token, data: dict[str, Any]) -> Token:
    for k, v in data.items():
        if v is not None:
            setattr(token, k, v)
    db.commit()
    db.refresh(token)
    return token


def soft_delete(db: Session, token: Token) -> Token:
    token.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(token)
    return token
