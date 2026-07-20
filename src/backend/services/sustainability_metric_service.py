import uuid
from typing import Any

from sqlalchemy.orm import Session

from src.backend.db.repositories.sustainability_metric_repo import (
    create_metric,
    delete_metric,
    get_metric,
    list_metrics,
    update_metric,
)


def create_metric_service(db: Session, data: dict[str, Any]) -> dict[str, Any]:
    metric = create_metric(
        db,
        project_id=data["project_id"],
        reference_id=data.get("reference_id"),
        recorded_date=data.get("recorded_date"),
        compliant_with_green_standards=data.get("compliant_with_green_standards"),
        energy_saved_kwh=data.get("energy_saved_kwh"),
        co2_avoided_tco2e=data.get("co2_avoided_tco2e"),
        lifecycle_cost_savings_inr=data.get("lifecycle_cost_savings_inr"),
        insulation_efficiency_ratio=data.get("insulation_efficiency_ratio"),
        payback_period_months=data.get("payback_period_months"),
        notes=data.get("notes"),
    )
    return _to_dict(metric)


def get_metric_service(db: Session, metric_id: uuid.UUID) -> dict[str, Any] | None:
    metric = get_metric(db, metric_id)
    return _to_dict(metric) if metric else None


def list_metrics_service(
    db: Session, project_id: uuid.UUID, reference_id: str | None = None
) -> list[dict[str, Any]]:
    metrics = list_metrics(db, project_id, reference_id)
    return [_to_dict(m) for m in metrics]


def update_metric_service(
    db: Session, metric_id: uuid.UUID, data: dict[str, Any]
) -> dict[str, Any] | None:
    metric = update_metric(db, metric_id, **data)
    return _to_dict(metric) if metric else None


def delete_metric_service(db: Session, metric_id: uuid.UUID) -> bool:
    return delete_metric(db, metric_id)


def _to_dict(metric) -> dict[str, Any]:
    return {
        "id": str(metric.id),
        "project_id": str(metric.project_id),
        "reference_id": metric.reference_id,
        "recorded_date": metric.recorded_date.isoformat() if metric.recorded_date else None,
        "compliant_with_green_standards": metric.compliant_with_green_standards,
        "energy_saved_kwh": metric.energy_saved_kwh,
        "co2_avoided_tco2e": metric.co2_avoided_tco2e,
        "lifecycle_cost_savings_inr": metric.lifecycle_cost_savings_inr,
        "insulation_efficiency_ratio": metric.insulation_efficiency_ratio,
        "payback_period_months": metric.payback_period_months,
        "notes": metric.notes,
        "created_at": metric.created_at.isoformat() if metric.created_at else None,
        "updated_at": metric.updated_at.isoformat() if metric.updated_at else None,
    }
