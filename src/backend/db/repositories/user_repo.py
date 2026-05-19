import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.backend.models.user import User


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()


def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()


def list_users(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[User], int]:
    query = db.query(User).filter(User.deleted_at.is_(None))

    if q:
        search = f"%{q}%"
        query = query.filter(User.email.ilike(search) | User.name.ilike(search))

    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()

    return list(items), total


def create(db: Session, email: str, name: str, password_hash: str, role: str) -> User:
    user = User(
        email=email,
        name=name,
        password_hash=password_hash,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user: User) -> User:
    db.commit()
    db.refresh(user)
    return user


def soft_delete(db: Session, user: User) -> User:
    user.deleted_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return user
