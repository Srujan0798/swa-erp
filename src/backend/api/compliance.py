import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.compliance import (
    ComplianceChecklistItemRead,
    ComplianceStandardRead,
    ComplianceSummaryResponse,
    ProjectComplianceItemRead,
    ProjectComplianceItemReview,
    ProjectComplianceItemUpdate,
)
from src.backend.services.compliance_service import (
    create_project_compliance_item_service,
    get_checklist_items_list,
    get_compliance_summary_service,
    get_project_items_list,
    get_standards_list,
    initialize_compliance,
    review_compliance_item_service,
    update_compliance_item_status_service,
)

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

projects_compliance_router = APIRouter(
    prefix="/api/projects/{project_id}/compliance", tags=["compliance"]
)


@router.post("/initialize", status_code=status.HTTP_200_OK)
def initialize(
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> dict:
    total = initialize_compliance(db)
    return {"message": "compliance initialized", "items_created": total}


@router.get("/standards", response_model=list[ComplianceStandardRead])
def list_standards(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> list[ComplianceStandardRead]:
    return get_standards_list(db)


@router.get("/standards/{standard_id}/checklist", response_model=list[ComplianceChecklistItemRead])
def list_checklist(
    standard_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> list[ComplianceChecklistItemRead]:
    return get_checklist_items_list(db, standard_id)


@router.patch("/items/{item_id}", response_model=ProjectComplianceItemRead)
def update_item(
    item_id: uuid.UUID,
    body: ProjectComplianceItemUpdate,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ProjectComplianceItemRead:
    try:
        result = update_compliance_item_status_service(
            db,
            item_id,
            status=body.status.value if body.status else None,
            evidence_document_id=body.evidence_document_id,
            notes=body.notes,
            actor_id=current_user.id,
        )
    except ValueError as e:
        if str(e) == "item_not_found":
            raise HTTPException(status_code=404, detail="Compliance item not found") from e
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ProjectComplianceItemRead(**result)


@router.post("/items/{item_id}/review", response_model=ProjectComplianceItemRead)
def review_item(
    item_id: uuid.UUID,
    body: ProjectComplianceItemReview,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ProjectComplianceItemRead:
    # Literal role membership, NOT hierarchy-based require_role(): compliance/certification
    # review is a segregation-of-duties action restricted to exactly Auditor or Designer per
    # the client's access matrix (resources/MEETINGS_MASTER.md Meeting 1 section 4) -
    # deliberately excludes PM even though PM is "senior" in the general role hierarchy, since
    # audit independence means the PM shouldn't be able to self-certify their own project.
    if current_user.role not in (Role.AUDITOR.value, Role.DESIGNER.value, Role.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Auditor or Designer can review compliance items",
        )
    try:
        result = review_compliance_item_service(db, item_id, current_user.id, body.notes)
    except ValueError as e:
        if str(e) == "item_not_found":
            raise HTTPException(status_code=404, detail="Compliance item not found") from e
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ProjectComplianceItemRead(**result)


# --- Project-scoped compliance endpoints ---


@projects_compliance_router.post(
    "/items", response_model=ProjectComplianceItemRead, status_code=status.HTTP_201_CREATED
)
def create_item(
    project_id: uuid.UUID,
    body: dict,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ProjectComplianceItemRead:
    checklist_item_id = body.get("checklist_item_id")
    if not checklist_item_id:
        raise HTTPException(status_code=422, detail="checklist_item_id required")
    try:
        result = create_project_compliance_item_service(
            db, project_id, uuid.UUID(str(checklist_item_id)), current_user.id
        )
    except ValueError as e:
        if str(e) == "checklist_item_not_found":
            raise HTTPException(status_code=404, detail="Checklist item not found") from e
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ProjectComplianceItemRead(**result)


@projects_compliance_router.post("/items/bulk/{standard_id}", status_code=status.HTTP_201_CREATED)
def bulk_create_items(
    project_id: uuid.UUID,
    standard_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> dict:
    from src.backend.db.repositories.compliance_repo import bulk_create_project_items

    items = bulk_create_project_items(db, project_id, standard_id)
    return {"items_created": len(items), "items": [str(i.id) for i in items]}


@projects_compliance_router.get("/items", response_model=list[ProjectComplianceItemRead])
def list_project_items(
    project_id: uuid.UUID,
    standard_id: uuid.UUID | None = Query(default=None),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> list[ProjectComplianceItemRead]:
    items = get_project_items_list(db, project_id, standard_id)
    return [ProjectComplianceItemRead(**i) for i in items]


@projects_compliance_router.get("/summary", response_model=ComplianceSummaryResponse)
def compliance_summary(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> ComplianceSummaryResponse:
    return get_compliance_summary_service(db, project_id)
