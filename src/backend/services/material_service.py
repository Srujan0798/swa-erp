import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.backend.db.repositories.audit_repo import create_entry
from src.backend.db.repositories.material_repo import (
    create_category as repo_create_category,
)
from src.backend.db.repositories.material_repo import (
    create_material as repo_create_material,
)
from src.backend.db.repositories.material_repo import (
    delete_category as repo_delete_category,
)
from src.backend.db.repositories.material_repo import (
    get_all_categories,
    get_by_id,
    get_category_by_id,
    has_children,
    has_materials,
    list_materials,
    soft_delete,
)
from src.backend.db.repositories.material_repo import (
    update_category as repo_update_category,
)
from src.backend.db.repositories.material_repo import (
    update_material as repo_update_material,
)
from src.backend.models.material import Material, MaterialCategory

# --- Category ---


def create_category(
    db: Session,
    data: dict[str, Any],
    actor_id: uuid.UUID,
) -> MaterialCategory:

    category = repo_create_category(db, data)

    create_entry(
        db,
        action="material_category.create",
        entity_type="material_category",
        user_id=actor_id,
        entity_id=category.id,
        after_json=_category_to_dict(category),
    )

    return category


def get_category_tree(db: Session) -> list[dict[str, Any]]:
    categories = get_all_categories(db)
    cat_map: dict[uuid.UUID, dict[str, Any]] = {}
    roots: list[dict[str, Any]] = []

    for c in categories:
        cat_map[c.id] = {
            "id": c.id,
            "name": c.name,
            "parent_id": c.parent_id,
            "created_at": c.created_at,
            "children": [],
        }

    for c in categories:
        node = cat_map[c.id]
        if c.parent_id and c.parent_id in cat_map:
            cat_map[c.parent_id]["children"].append(node)
        else:
            roots.append(node)

    return roots


def update_category(
    db: Session,
    category_id: uuid.UUID,
    data: dict[str, Any],
    actor_id: uuid.UUID,
) -> MaterialCategory | None:
    category = get_category_by_id(db, category_id)
    if not category:
        return None

    before = _category_to_dict(category)

    updated = repo_update_category(db, category_id, data)
    if not updated:
        return None

    create_entry(
        db,
        action="material_category.update",
        entity_type="material_category",
        user_id=actor_id,
        entity_id=category_id,
        before_json=before,
        after_json=_category_to_dict(updated),
    )

    return updated


def delete_category(
    db: Session,
    category_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> bool:
    category = get_category_by_id(db, category_id)
    if not category:
        return False

    if has_children(db, category_id):
        raise ValueError("Cannot delete category with children")

    if has_materials(db, category_id):
        raise ValueError("Cannot delete category with materials")

    before = _category_to_dict(category)

    success = repo_delete_category(db, category_id)
    if success:
        create_entry(
            db,
            action="material_category.delete",
            entity_type="material_category",
            user_id=actor_id,
            entity_id=category_id,
            before_json=before,
        )

    return success


# --- Material ---


def create_material(
    db: Session,
    data: dict[str, Any],
    actor_id: uuid.UUID,
) -> Material:
    material = repo_create_material(db, data)

    create_entry(
        db,
        action="material.create",
        entity_type="material",
        user_id=actor_id,
        entity_id=material.id,
        after_json=_material_to_dict(material),
    )

    return material


def get_material(db: Session, material_id: uuid.UUID) -> dict[str, Any] | None:
    material = get_by_id(db, material_id)
    if not material:
        return None

    category_name = None
    if material.category_id:
        cat = get_category_by_id(db, material.category_id)
        category_name = cat.name if cat else None

    return {
        "id": material.id,
        "name": material.name,
        "code": material.code,
        "description": material.description,
        "category_id": material.category_id,
        "unit": material.unit,
        "is_active": material.is_active,
        "created_at": material.created_at,
        "category_name": category_name,
    }


def list_materials_service(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    category_id: uuid.UUID | None = None,
    is_active: bool | None = None,
) -> tuple[list[dict[str, Any]], int, int, int]:
    items, total, page, page_size = list_materials(
        db, page=page, page_size=page_size, search=search,
        category_id=category_id, is_active=is_active,
    )

    result = []
    for m in items:
        category_name = None
        if m.category_id:
            cat = get_category_by_id(db, m.category_id)
            category_name = cat.name if cat else None
        result.append({
            "id": m.id,
            "name": m.name,
            "code": m.code,
            "description": m.description,
            "category_id": m.category_id,
            "unit": m.unit,
            "is_active": m.is_active,
            "created_at": m.created_at,
            "category_name": category_name,
        })

    return result, total, page, page_size


def update_material(
    db: Session,
    material_id: uuid.UUID,
    data: dict[str, Any],
    actor_id: uuid.UUID,
) -> Material | None:
    material = get_by_id(db, material_id)
    if not material:
        return None

    before = _material_to_dict(material)

    updated = repo_update_material(db, material_id, data)
    if not updated:
        return None

    create_entry(
        db,
        action="material.update",
        entity_type="material",
        user_id=actor_id,
        entity_id=material_id,
        before_json=before,
        after_json=_material_to_dict(updated),
    )

    return updated


def delete_material(
    db: Session,
    material_id: uuid.UUID,
    actor_id: uuid.UUID,
) -> bool:
    material = get_by_id(db, material_id)
    if not material:
        return False

    before = _material_to_dict(material)
    success = soft_delete(db, material_id)

    if success:
        create_entry(
            db,
            action="material.delete",
            entity_type="material",
            user_id=actor_id,
            entity_id=material_id,
            before_json=before,
        )

    return success


def _category_to_dict(category) -> dict[str, Any]:
    return {
        "id": str(category.id),
        "name": category.name,
        "parent_id": str(category.parent_id) if category.parent_id else None,
    }


def _material_to_dict(material) -> dict[str, Any]:
    return {
        "id": str(material.id),
        "name": material.name,
        "code": material.code,
        "description": material.description,
        "category_id": str(material.category_id) if material.category_id else None,
        "unit": material.unit,
        "is_active": material.is_active,
    }
