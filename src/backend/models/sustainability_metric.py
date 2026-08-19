import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.db.base import Base


class SustainabilityMetric(Base):
    __tablename__ = "sustainability_metrics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True
    )
    reference_id: Mapped[str | None] = mapped_column(String(30), nullable=True)
    recorded_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    compliant_with_green_standards: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    energy_saved_kwh: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    co2_avoided_tco2e: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    lifecycle_cost_savings_inr: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    insulation_efficiency_ratio: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    payback_period_months: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
