import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.backend.models.material import Material, MaterialCategory

# --- Category ---


def create_category(db: Session, data: dict[str, Any]) -> MaterialCategory:
    category = MaterialCategory(**data)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category_by_id(db: Session, category_id: uuid.UUID) -> MaterialCategory | None:
    return db.query(MaterialCategory).filter(MaterialCategory.id == category_id).first()


def get_all_categories(db: Session) -> list[MaterialCategory]:
    return db.query(MaterialCategory).order_by(MaterialCategory.name).all()


def update_category(
    db: Session, category_id: uuid.UUID, data: dict[str, Any]
) -> MaterialCategory | None:
    category = get_category_by_id(db, category_id)
    if not category:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: uuid.UUID) -> bool:
    category = get_category_by_id(db, category_id)
    if not category:
        return False
    db.delete(category)
    db.commit()
    return True


def has_children(db: Session, category_id: uuid.UUID) -> bool:
    return (
        db.query(MaterialCategory)
        .filter(MaterialCategory.parent_id == category_id)
        .count()
        > 0
    )


def has_materials(db: Session, category_id: uuid.UUID) -> bool:
    return (
        db.query(Material).filter(Material.category_id == category_id).count() > 0
    )


# --- Material ---


def create_material(db: Session, data: dict[str, Any]) -> Material:
    material = Material(**data)
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def get_by_id(db: Session, material_id: uuid.UUID) -> Material | None:
    return (
        db.query(Material)
        .filter(Material.id == material_id, Material.deleted_at.is_(None))
        .first()
    )


def get_by_code(db: Session, code: str) -> Material | None:
    return db.query(Material).filter(Material.code == code).first()


def list_materials(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    category_id: uuid.UUID | None = None,
    is_active: bool | None = None,
) -> tuple[list[Material], int, int, int]:
    query = db.query(Material).filter(Material.deleted_at.is_(None))

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Material.name.ilike(term),
                Material.code.ilike(term),
                Material.description.ilike(term),
            )
        )

    if category_id is not None:
        query = query.filter(Material.category_id == category_id)

    if is_active is not None:
        query = query.filter(Material.is_active == is_active)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Material.created_at.desc()).offset(offset).limit(page_size).all()

    return items, total, page, page_size


def update_material(
    db: Session, material_id: uuid.UUID, data: dict[str, Any]
) -> Material | None:
    material = get_by_id(db, material_id)
    if not material:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(material, key, value)
    db.commit()
    db.refresh(material)
    return material


def soft_delete(db: Session, material_id: uuid.UUID) -> bool:
    material = get_by_id(db, material_id)
    if not material:
        return False
    material.deleted_at = datetime.utcnow()
    db.commit()
    return True
