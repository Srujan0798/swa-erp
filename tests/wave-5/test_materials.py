import uuid

import pytest


# ---------------------------------------------------------------------------
# Material Categories
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_material_category(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/material-categories",
        json={"name": "Structural"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Structural"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_category_with_parent(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/material-categories",
        json={"name": "Concrete"},
    )
    parent_id = r.json()["id"]

    r2 = await authed_admin_client.post(
        "/api/material-categories",
        json={"name": "Ready Mix", "parent_id": parent_id},
    )
    assert r2.status_code == 201
    assert r2.json()["parent_id"] == parent_id


@pytest.mark.asyncio
async def test_list_category_tree(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/material-categories",
        json={"name": "Electrical"},
    )
    parent_id = r.json()["id"]

    await authed_admin_client.post(
        "/api/material-categories",
        json={"name": "Cables", "parent_id": parent_id},
    )

    r = await authed_admin_client.get("/api/material-categories")
    assert r.status_code == 200
    tree = r.json()
    assert len(tree) >= 1
    electrical = [c for c in tree if c["name"] == "Electrical"]
    assert len(electrical) == 1
    assert len(electrical[0]["children"]) >= 1


@pytest.mark.asyncio
async def test_update_material_category(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/material-categories",
        json={"name": "Old Name"},
    )
    cat_id = r.json()["id"]

    r = await authed_admin_client.put(
        f"/api/material-categories/{cat_id}",
        json={"name": "New Name"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_update_category_not_found(authed_admin_client):
    fake_id = str(uuid.uuid4())
    r = await authed_admin_client.put(f"/api/material-categories/{fake_id}", json={"name": "X"})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_material_category(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/material-categories",
        json={"name": "To Delete"},
    )
    cat_id = r.json()["id"]

    r = await authed_admin_client.delete(f"/api/material-categories/{cat_id}")
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_delete_category_with_children_fails(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/material-categories",
        json={"name": "Parent Cat"},
    )
    parent_id = r.json()["id"]

    await authed_admin_client.post(
        "/api/material-categories",
        json={"name": "Child Cat", "parent_id": parent_id},
    )

    r = await authed_admin_client.delete(f"/api/material-categories/{parent_id}")
    assert r.status_code == 409


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_material(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/materials",
        json={
            "name": "TMT Steel Bars",
            "code": f"MAT-{uuid.uuid4().hex[:6]}",
            "description": "Fe 500 grade",
            "unit": "kg",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "TMT Steel Bars"
    assert data["unit"] == "kg"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_material_with_category(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/material-categories",
        json={"name": "Steel"},
    )
    cat_id = r.json()["id"]

    r = await authed_admin_client.post(
        "/api/materials",
        json={
            "name": "Steel Rod",
            "code": f"MAT-{uuid.uuid4().hex[:6]}",
            "unit": "nos",
            "category_id": cat_id,
        },
    )
    assert r.status_code == 201
    assert r.json()["category_id"] == cat_id
    assert r.json()["category_name"] == "Steel"


@pytest.mark.asyncio
async def test_create_material_duplicate_code(authed_admin_client):
    code = f"M-{uuid.uuid4().hex[:6]}"
    await authed_admin_client.post(
        "/api/materials",
        json={"name": "Mat A", "code": code, "unit": "kg"},
    )
    r = await authed_admin_client.post(
        "/api/materials",
        json={"name": "Mat B", "code": code, "unit": "kg"},
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_list_materials(authed_admin_client):
    code1 = f"MAT-{uuid.uuid4().hex[:6]}"
    code2 = f"MAT-{uuid.uuid4().hex[:6]}"
    await authed_admin_client.post("/api/materials", json={"name": "Material 1", "code": code1, "unit": "kg"})
    await authed_admin_client.post("/api/materials", json={"name": "Material 2", "code": code2, "unit": "nos"})

    r = await authed_admin_client.get("/api/materials")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 2
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_list_materials_search(authed_admin_client):
    unique = uuid.uuid4().hex[:8]
    code = f"M-{unique}"
    await authed_admin_client.post(
        "/api/materials",
        json={"name": f"Unique Material {unique}", "code": code, "unit": "kg"},
    )
    r = await authed_admin_client.get(f"/api/materials?search={unique}")
    assert r.status_code == 200
    assert r.json()["total"] >= 1


@pytest.mark.asyncio
async def test_list_materials_filter_category(authed_admin_client):
    r = await authed_admin_client.post(
        "/api/material-categories",
        json={"name": "Filter Cat"},
    )
    cat_id = r.json()["id"]

    code = f"MAT-{uuid.uuid4().hex[:6]}"
    await authed_admin_client.post(
        "/api/materials",
        json={"name": "Cat Material", "code": code, "unit": "kg", "category_id": cat_id},
    )

    r = await authed_admin_client.get(f"/api/materials?category_id={cat_id}")
    assert r.status_code == 200
    assert r.json()["total"] >= 1


@pytest.mark.asyncio
async def test_get_material(authed_admin_client):
    code = f"MAT-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/materials",
        json={"name": "Get Mat", "code": code, "unit": "nos"},
    )
    mat_id = r.json()["id"]

    r = await authed_admin_client.get(f"/api/materials/{mat_id}")
    assert r.status_code == 200
    assert r.json()["code"] == code


@pytest.mark.asyncio
async def test_get_material_not_found(authed_admin_client):
    r = await authed_admin_client.get(f"/api/materials/{uuid.uuid4()}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_material(authed_admin_client):
    code = f"MAT-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/materials",
        json={"name": "Original", "code": code, "unit": "kg"},
    )
    mat_id = r.json()["id"]

    r = await authed_admin_client.put(
        f"/api/materials/{mat_id}",
        json={"name": "Updated", "unit": "nos"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Updated"
    assert r.json()["unit"] == "nos"


@pytest.mark.asyncio
async def test_delete_material(authed_admin_client):
    code = f"MAT-{uuid.uuid4().hex[:6]}"
    r = await authed_admin_client.post(
        "/api/materials",
        json={"name": "To Delete", "code": code, "unit": "kg"},
    )
    mat_id = r.json()["id"]

    r = await authed_admin_client.delete(f"/api/materials/{mat_id}")
    assert r.status_code == 204

    # Verify soft deleted
    r = await authed_admin_client.get(f"/api/materials/{mat_id}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_delete_material_not_found(authed_admin_client):
    r = await authed_admin_client.delete(f"/api/materials/{uuid.uuid4()}")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Role-based access
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_viewer_cannot_create_material(authed_viewer_client):
    r = await authed_viewer_client.post(
        "/api/materials",
        json={"name": "Fail", "code": "F-1", "unit": "kg"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_viewer_can_list_materials(authed_viewer_client, authed_admin_client):
    code = f"MAT-{uuid.uuid4().hex[:6]}"
    await authed_admin_client.post("/api/materials", json={"name": "Viewable", "code": code, "unit": "kg"})

    r = await authed_viewer_client.get("/api/materials")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_viewer_cannot_create_category(authed_viewer_client):
    r = await authed_viewer_client.post(
        "/api/material-categories",
        json={"name": "Fail Cat"},
    )
    assert r.status_code == 403
