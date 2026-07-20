import uuid

from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.backend.models.sustainability_metric import SustainabilityMetric


def create_metric(
    db: Session,
    project_id: uuid.UUID,
    reference_id: str | None,
    recorded_date,
    compliant_with_green_standards: bool | None,
    energy_saved_kwh,
    co2_avoided_tco2e,
    lifecycle_cost_savings_inr,
    insulation_efficiency_ratio,
    payback_period_months,
    notes: str | None,
) -> SustainabilityMetric:
    metric = SustainabilityMetric(
        project_id=project_id,
        reference_id=reference_id,
        recorded_date=recorded_date,
        compliant_with_green_standards=compliant_with_green_standards,
        energy_saved_kwh=energy_saved_kwh,
        co2_avoided_tco2e=co2_avoided_tco2e,
        lifecycle_cost_savings_inr=lifecycle_cost_savings_inr,
        insulation_efficiency_ratio=insulation_efficiency_ratio,
        payback_period_months=payback_period_months,
        notes=notes,
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def get_metric(db: Session, metric_id: uuid.UUID) -> SustainabilityMetric | None:
    return db.query(SustainabilityMetric).filter(SustainabilityMetric.id == metric_id).first()


def list_metrics(
    db: Session, project_id: uuid.UUID, reference_id: str | None = None
) -> list[SustainabilityMetric]:
    query = db.query(SustainabilityMetric).filter(
        SustainabilityMetric.project_id == project_id
    )
    if reference_id:
        query = query.filter(SustainabilityMetric.reference_id == reference_id)
    return query.order_by(desc(SustainabilityMetric.recorded_date)).all()


def update_metric(
    db: Session, metric_id: uuid.UUID, **kwargs
) -> SustainabilityMetric | None:
    metric = get_metric(db, metric_id)
    if not metric:
        return None
    for key, value in kwargs.items():
        if value is not None:
            setattr(metric, key, value)
    db.commit()
    db.refresh(metric)
    return metric


def delete_metric(db: Session, metric_id: uuid.UUID) -> bool:
    metric = get_metric(db, metric_id)
    if not metric:
        return False
    db.delete(metric)
    db.commit()
    return True
