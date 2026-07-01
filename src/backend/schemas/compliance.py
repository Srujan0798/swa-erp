import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ComplianceStatus(StrEnum):
    PENDING = "pending"
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NA = "na"


class ComplianceStandardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    version: str
    description: str | None


class ComplianceChecklistItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    standard_id: uuid.UUID
    category: str
    requirement: str
    description: str | None
    is_mandatory: bool


class ComplianceChecklistItemCreate(BaseModel):
    standard_id: uuid.UUID
    category: str
    requirement: str
    description: str | None = None
    is_mandatory: bool = True


class ProjectComplianceItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    checklist_item_id: uuid.UUID
    status: ComplianceStatus
    evidence_document_id: uuid.UUID | None
    notes: str | None
    reviewed_by: uuid.UUID | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    standard_name: str | None = None
    category: str | None = None
    requirement: str | None = None
    is_mandatory: bool | None = None


class ProjectComplianceItemUpdate(BaseModel):
    status: ComplianceStatus | None = None
    evidence_document_id: uuid.UUID | None = None
    notes: str | None = None


class ProjectComplianceItemReview(BaseModel):
    notes: str | None = None


class ComplianceDashboardResponse(BaseModel):
    standard_name: str
    total_items: int
    compliant_count: int
    non_compliant_count: int
    pending_count: int
    na_count: int
    compliance_percentage: float


class ComplianceSummaryResponse(BaseModel):
    project_id: uuid.UUID
    standards: list[ComplianceDashboardResponse]
    overall_percentage: float
