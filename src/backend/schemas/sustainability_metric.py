import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SustainabilityMetricCreate(BaseModel):
    project_id: uuid.UUID
    reference_id: str | None = None
    recorded_date: date | None = None
    compliant_with_green_standards: bool | None = None
    energy_saved_kwh: Decimal | None = None
    co2_avoided_tco2e: Decimal | None = None
    lifecycle_cost_savings_inr: Decimal | None = None
    insulation_efficiency_ratio: Decimal | None = None
    payback_period_months: Decimal | None = None
    notes: str | None = None


class SustainabilityMetricUpdate(BaseModel):
    reference_id: str | None = None
    recorded_date: date | None = None
    compliant_with_green_standards: bool | None = None
    energy_saved_kwh: Decimal | None = None
    co2_avoided_tco2e: Decimal | None = None
    lifecycle_cost_savings_inr: Decimal | None = None
    insulation_efficiency_ratio: Decimal | None = None
    payback_period_months: Decimal | None = None
    notes: str | None = None


class SustainabilityMetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    reference_id: str | None
    recorded_date: date | None
    compliant_with_green_standards: bool | None
    energy_saved_kwh: Decimal | None
    co2_avoided_tco2e: Decimal | None
    lifecycle_cost_savings_inr: Decimal | None
    insulation_efficiency_ratio: Decimal | None
    payback_period_months: Decimal | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
