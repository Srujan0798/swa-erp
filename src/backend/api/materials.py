import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.backend.core.deps import require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.material import (
    MaterialCategoryCreate,
    MaterialCategoryRead,
    MaterialCategoryTree,
    MaterialCategoryUpdate,
    MaterialCreate,
    MaterialListResponse,
    MaterialRead,
    MaterialUpdate,
)
from src.backend.services.material_service import (
    create_category,
    create_material,
    delete_category,
    delete_material,
    get_category_tree,
    get_material,
    list_materials_service,
    update_category,
    update_material,
)

router = APIRouter(tags=["materials"])


# --- Category endpoints ---


@router.post(
    "/api/material-categories",
    response_model=MaterialCategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_material_category(
    body: MaterialCategoryCreate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> MaterialCategoryRead:
    category = create_category(db, body.model_dump(), current_user.id)
    return MaterialCategoryRead.model_validate(category)


@router.get("/api/material-categories", response_model=list[MaterialCategoryTree])
def list_material_categories(
    db: Session = Depends(get_db),  # noqa: B008
) -> list[MaterialCategoryTree]:
    tree = get_category_tree(db)
    return [MaterialCategoryTree.model_validate(node) for node in tree]


@router.put(
    "/api/material-categories/{category_id}",
    response_model=MaterialCategoryRead,
)
def update_material_category(
    category_id: uuid.UUID,
    body: MaterialCategoryUpdate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> MaterialCategoryRead:
    updated = update_category(db, category_id, body.model_dump(exclude_unset=True), current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return MaterialCategoryRead.model_validate(updated)


@router.delete(
    "/api/material-categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_material_category(
    category_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    try:
        success = delete_category(db, category_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")


# --- Material endpoints ---


@router.post(
    "/api/materials",
    response_model=MaterialRead,
    status_code=status.HTTP_201_CREATED,
)
def create_material_endpoint(
    body: MaterialCreate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> MaterialRead:
    try:
        material = create_material(db, body.model_dump(), current_user.id)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Material code already exists") from e
    result = get_material(db, material.id)
    return MaterialRead.model_validate(result)


@router.get("/api/materials", response_model=MaterialListResponse)
def list_materials(
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = None,
    category_id: uuid.UUID | None = None,
    is_active: bool | None = None,
) -> MaterialListResponse:
    items, total, page, page_size = list_materials_service(
        db, page=page, page_size=page_size, search=search,
        category_id=category_id, is_active=is_active,
    )
    result = [MaterialRead.model_validate(item) for item in items]
    return MaterialListResponse(items=result, total=total, page=page, page_size=page_size)


@router.get("/api/materials/{material_id}", response_model=MaterialRead)
def get_material_endpoint(
    material_id: uuid.UUID,
    db: Session = Depends(get_db),  # noqa: B008
) -> MaterialRead:
    result = get_material(db, material_id)
    if not result:
        raise HTTPException(status_code=404, detail="Material not found")
    return MaterialRead.model_validate(result)


@router.put("/api/materials/{material_id}", response_model=MaterialRead)
def update_material_endpoint(
    material_id: uuid.UUID,
    body: MaterialUpdate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> MaterialRead:
    try:
        updated = update_material(
            db, material_id, body.model_dump(exclude_unset=True), current_user.id
        )
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Material code already exists") from e
    if not updated:
        raise HTTPException(status_code=404, detail="Material not found")
    result = get_material(db, material_id)
    return MaterialRead.model_validate(result)


@router.delete(
    "/api/materials/{material_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_material_endpoint(
    material_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = delete_material(db, material_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Material not found")
