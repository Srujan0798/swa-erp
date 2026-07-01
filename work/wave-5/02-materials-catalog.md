# Task 02 — Materials Catalog & Categories

## Goal
Create the Material and MaterialCategory models for a searchable materials catalog. Categories support a tree structure (parent-child). Materials are linked to categories and used in RFQs and BOQs.

## Files to Create/Modify

### 1. Models
Create `src/backend/models/material.py`:
```python
class MaterialCategory(Base):
    __tablename__ = "material_categories"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("material_categories.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Material(Base):
    __tablename__ = "materials"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("material_categories.id"), nullable=True, index=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

Register both models in `src/backend/models/__init__.py`.

### 2. Schemas
Create `src/backend/schemas/material.py`:
- `MaterialCategoryCreate` — name, parent_id (optional)
- `MaterialCategoryRead` — id, name, parent_id, children (recursive, optional)
- `MaterialCreate` — name, code, description, category_id, unit
- `MaterialUpdate` — all fields optional
- `MaterialRead` — full material with category name
- `MaterialListResponse` — paginated list
- `MaterialCategoryTree` — nested tree response for categories

### 3. Repository
Create `src/backend/db/repositories/material_repo.py`:
- `create_category(db, data)` — create category
- `get_category_tree(db)` — returns all categories as nested tree
- `get_category_by_id(db, category_id)` — single category
- `update_category(db, category_id, data)` — update category
- `delete_category(db, category_id)` — hard delete (only if no children or materials)
- `create_material(db, data)` — create material
- `get_by_id(db, material_id)` — material with category
- `get_by_code(db, code)` — unique lookup
- `list_materials(db, page, page_size, search, category_id, is_active)` — paginated, soft-delete excluded. Search matches name, code, description
- `update_material(db, material_id, data)` — partial update
- `soft_delete(db, material_id)` — set deleted_at

### 4. Service
Create `src/backend/services/material_service.py`:
- `create_category(db, data)` — create + audit log "material_category.create"
- `get_category_tree(db)` — build nested tree from flat query
- `update_category(db, category_id, data)` — update + audit
- `delete_category(db, category_id)` — validate no children/materials, delete + audit
- `create_material(db, data)` — create + audit log "material.create"
- `update_material(db, material_id, data)` — update + audit
- `get_material(db, material_id)` — return with category
- `list_materials(db, page, page_size, search, category_id, is_active)` — paginated
- `delete_material(db, material_id)` — soft delete + audit

### 5. API
Create `src/backend/api/materials.py`:
- `POST /api/material-categories` — create category
- `GET /api/material-categories` — get category tree
- `PUT /api/material-categories/{category_id}` — update category
- `DELETE /api/material-categories/{category_id}` — delete category
- `POST /api/materials` — create material (require admin or PM)
- `GET /api/materials` — list materials, query: page, page_size, search, category_id, is_active
- `GET /api/materials/{material_id}` — get material
- `PUT /api/materials/{material_id}` — update material
- `DELETE /api/materials/{material_id}` — soft delete

Register router in `src/backend/main.py` with prefix `/api/materials` and `/api/material-categories`.

### 6. Migration
Create `src/backend/alembic/versions/0008_add_materials.py` — creates `material_categories` and `materials` tables.

## Files you must NOT touch
- `src/backend/models/vendor.py` (from Task 01)
- `src/backend/main.py` (only add router imports)

## Acceptance Criteria
- [ ] `pytest tests/wave-5/test_materials.py` passes
- [ ] `make lint` clean
- [ ] Can create categories with parent-child nesting
- [ ] Category tree endpoint returns nested structure
- [ ] Cannot delete category with children or materials (409)
- [ ] Can create materials with category assignment
- [ ] Material code is unique; duplicate returns 409
- [ ] Search filters by name, code, description (case-insensitive)
- [ ] Category filter works: materials in specific category
- [ ] Soft-deleted materials excluded from queries

## Test File
Create `tests/wave-5/test_materials.py` with at least:
- `test_create_category` — create root category
- `test_create_nested_category` — create child category
- `test_category_tree` — verify nested tree structure
- `test_delete_category_with_children` — expect 409
- `test_create_material` — create with category
- `test_create_material_duplicate_code` — expect 409
- `test_list_materials_search` — search by name
- `test_list_materials_filter_by_category` — filter by category_id
- `test_update_material` — update unit and description
- `test_soft_delete_material` — verify excluded from list

## Notes
- Unit field: common values are "nos", "kg", "sqm", "cum", "rmt", "ls" (lump sum)
- Category tree: build in Python from flat DB query (no CTE needed at this scale)
- Material code: auto-generate from category prefix + sequence if not provided (e.g., "ELE-001")
- Consider adding `brand` and `specification` fields later; keep schema extensible
