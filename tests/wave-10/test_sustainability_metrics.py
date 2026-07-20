async def test_create_sustainability_metric(authed_pm_client, test_project):
    project_id = str(test_project.id)
    payload = {
        "project_id": project_id,
        "reference_id": "SWA-2025-PRJ-065",
        "recorded_date": "2025-06-01",
        "compliant_with_green_standards": False,
        "energy_saved_kwh": "1200.50",
        "co2_avoided_tco2e": "3.25",
        "lifecycle_cost_savings_inr": "450000.00",
        "insulation_efficiency_ratio": "0.89",
        "payback_period_months": "18.00",
        "notes": "Sample green-building entry",
    }
    r = await authed_pm_client.post(
        f"/api/projects/{project_id}/sustainability/metrics", json=payload
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["reference_id"] == "SWA-2025-PRJ-065"
    assert data["compliant_with_green_standards"] is False
    assert data["insulation_efficiency_ratio"] == 0.89 or data["insulation_efficiency_ratio"] == "0.89"
    assert data["project_id"] == project_id
    return data["id"]


async def test_list_sustainability_metrics_scoped_by_project(authed_pm_client, test_project, db_session):
    from src.backend.models.sustainability_metric import SustainabilityMetric

    project_id = str(test_project.id)
    await authed_pm_client.post(
        f"/api/projects/{project_id}/sustainability/metrics",
        json={"project_id": project_id,
        "reference_id": "SWA-2025-PRJ-065", "energy_saved_kwh": "100.00"},
    )

    other = SustainabilityMetric(project_id=test_project.id, reference_id="OTHER", energy_saved_kwh=None)
    db_session.add(other)
    db_session.commit()

    r = await authed_pm_client.get(
        f"/api/projects/{project_id}/sustainability/metrics"
    )
    assert r.status_code == 200, r.text
    items = r.json()
    assert len(items) >= 1
    assert all(i["project_id"] == project_id for i in items)


async def test_update_sustainability_metric(authed_pm_client, test_project):
    project_id = str(test_project.id)
    created = await authed_pm_client.post(
        f"/api/projects/{project_id}/sustainability/metrics",
        json={"project_id": project_id,
        "reference_id": "SWA-2025-PRJ-065", "compliant_with_green_standards": False},
    )
    metric_id = created.json()["id"]

    r = await authed_pm_client.patch(
        f"/api/projects/{project_id}/sustainability/metrics/{metric_id}",
        json={"compliant_with_green_standards": True, "payback_period_months": "24.00"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["compliant_with_green_standards"] is True


async def test_delete_sustainability_metric(authed_pm_client, test_project):
    project_id = str(test_project.id)
    created = await authed_pm_client.post(
        f"/api/projects/{project_id}/sustainability/metrics",
        json={"project_id": project_id, "reference_id": "SWA-2025-PRJ-065"},
    )
    metric_id = created.json()["id"]

    r = await authed_pm_client.delete(
        f"/api/projects/{project_id}/sustainability/metrics/{metric_id}"
    )
    assert r.status_code == 204, r.text

    r = await authed_pm_client.get(
        f"/api/projects/{project_id}/sustainability/metrics/{metric_id}"
    )
    assert r.status_code == 404


async def test_create_requires_pm_role(authed_viewer_client, test_project):
    project_id = str(test_project.id)
    r = await authed_viewer_client.post(
        f"/api/projects/{project_id}/sustainability/metrics",
        json={"project_id": project_id, "reference_id": "SWA-2025-PRJ-065"},
    )
    assert r.status_code == 403
