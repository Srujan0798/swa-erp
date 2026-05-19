import uuid

from sqlalchemy.orm import Session

from src.backend.core.security import hash_password
from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.user_repo import create as create_user
from src.backend.db.repositories.user_repo import get_by_id, list_users
from src.backend.db.repositories.user_repo import soft_delete as soft_delete_user
from src.backend.db.repositories.user_repo import update as update_user
from src.backend.models.user import User
from src.backend.schemas.user import UserCreate, UserUpdate


def list_users_service(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[User], int, int, int]:
    items, total = list_users(db, page, page_size, q, role, is_active)
    return items, total, page, page_size


def create_user_service(db: Session, data: UserCreate, actor_id: uuid.UUID | None) -> User:
    password_hash = hash_password(data.password)
    user = create_user(db, data.email, data.name, password_hash, data.role.value)

    create_entry(
        db,
        action="user.create",
        entity_type="user",
        entity_id=user.id,
        user_id=actor_id,
        after_json={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
        },
    )

    return user


def get_user_service(db: Session, user_id: uuid.UUID) -> User | None:
    return get_by_id(db, user_id)


def update_user_service(
    db: Session,
    user_id: uuid.UUID,
    data: UserUpdate,
    actor_id: uuid.UUID,
    is_self: bool = False,
) -> User | None:
    user = get_by_id(db, user_id)
    if not user:
        return None

    before_json = {
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
    }

    if data.name is not None:
        user.name = data.name
    if data.role is not None:
        if is_self:
            return None
        user.role = data.role
    if data.is_active is not None:
        if is_self:
            return None
        user.is_active = data.is_active

    update_user(db, user)

    after_json = {
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active,
    }

    create_entry(
        db,
        action="user.update",
        entity_type="user",
        entity_id=user.id,
        user_id=actor_id,
        before_json=before_json,
        after_json=after_json,
    )

    return user


def soft_delete_user_service(
    db: Session,
    user_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> bool:
    user = get_by_id(db, user_id)
    if not user:
        return False

    before_json = {
        "deleted_at": None,
    }

    soft_delete_user(db, user)

    after_json = {
        "deleted_at": str(user.deleted_at),
    }

    create_entry(
        db,
        action="user.delete",
        entity_type="user",
        entity_id=user.id,
        user_id=actor_id,
        before_json=before_json,
        after_json=after_json,
    )

    return True
