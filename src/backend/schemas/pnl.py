import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProjectCostCreate(BaseModel):
    project_id: uuid.UUID
    category: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=2000)
    amount: Decimal = Field(ge=0)
    quantity: Decimal | None = Field(default=None, gt=0)
    rate: Decimal | None = Field(default=None, ge=0)
    reference_id: uuid.UUID | None = None
    reference_type: str | None = Field(default=None, max_length=50)
    date: date


class ProjectCostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    category: str
    description: str
    amount: Decimal
    quantity: Decimal | None
    rate: Decimal | None
    reference_id: uuid.UUID | None
    reference_type: str | None
    date: date
    created_by: uuid.UUID
    created_at: datetime
    created_by_name: str | None = None


class ProjectCostListResponse(BaseModel):
    items: list[ProjectCostRead]
    total: int
    page: int
    page_size: int


class CostBreakdownItem(BaseModel):
    category: str
    amount: Decimal
    count: int
    percentage: Decimal


class ProjectPnLSummary(BaseModel):
    project_id: uuid.UUID
    project_name: str | None = None
    total_revenue: Decimal
    total_costs: Decimal
    net_profit: Decimal
    margin_pct: Decimal
    cost_breakdown: list[CostBreakdownItem]
