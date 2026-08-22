import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.repositories.project_repo import get_by_id as get_project_by_id
from src.backend.db.session import get_db
from src.backend.models.document_reference import DocumentReference
from src.backend.models.user import User
from src.backend.schemas.document_reference import (
    DocumentReferenceCounters,
    DocumentReferenceCreate,
    DocumentReferenceListResponse,
    DocumentReferenceRead,
    DocumentReferenceUpdate,
)
from src.backend.services.document_reference_service import (
    ProjectNotFoundError,
    TokenNotFoundError,
    create_document_reference_service,
    get_document_reference_service,
    list_document_references_service,
    soft_delete_document_reference_service,
    update_document_reference_service,
)
from src.backend.services.reference_id_service import get_current_seq

router = APIRouter(prefix="/api/document-references", tags=["document-references"])


def _to_read(db: Session, doc: DocumentReference) -> DocumentReferenceRead:
    read = DocumentReferenceRead.model_validate(doc)
    project = get_project_by_id(db, doc.project_id)
    if project is not None:
        read.project_code = project.code
    return read


@router.get("", response_model=DocumentReferenceListResponse)
def list_document_references(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    project_id: uuid.UUID | None = None,
    token_id: uuid.UUID | None = None,
    document_type: str | None = None,
    q: str | None = None,
) -> DocumentReferenceListResponse:
    items, total, page, page_size = list_document_references_service(
        db,
        page=page,
        page_size=page_size,
        project_id=project_id,
        token_id=token_id,
        document_type=document_type,
        q=q,
    )
    return DocumentReferenceListResponse(
        items=[_to_read(db, d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/counters", response_model=DocumentReferenceCounters)
def get_document_reference_counters(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentReferenceCounters:
    """Expose DBR/KDR shared counter so the sheet mental model is visible in UI."""
    year = datetime.now(UTC).year
    last = get_current_seq(db, "DBR", year=year)
    next_seq = last + 1
    return DocumentReferenceCounters(
        year=year,
        dbr_kdr_last_seq=last,
        dbr_kdr_next_preview=f"SWA-{year}-DBR-{next_seq:03d}",
    )


@router.post(
    "",
    response_model=DocumentReferenceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_document_reference(
    body: DocumentReferenceCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentReferenceRead:
    # Type-conditional access control per the client's access matrix
    # (resources/MEETINGS_MASTER.md Meeting 1 section 4):
    #   DBR/KDR generation -> PM, Designer
    #   Reforge/DPR -> Auditor, Designer
    #   anything else -> PM only (safe default)
    doc_type = (body.document_type or "").strip().upper()
    if doc_type in ("DBR", "KDR"):
        allowed = {Role.PM.value, Role.DESIGNER.value}
    elif doc_type == "REFORGE":
        # Literal membership, not hierarchy: excludes PM even though PM is "senior" in the
        # general role hierarchy - Reforge/certification is a segregation-of-duties action
        # restricted to exactly Auditor or Designer per the client's matrix (audit
        # independence: PM shouldn't self-certify their own project).
        allowed = {Role.AUDITOR.value, Role.DESIGNER.value}
    else:
        allowed = {Role.PM.value}
    if current_user.role not in allowed and current_user.role != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{current_user.role}' cannot create a '{doc_type or body.document_type}' document reference",
        )
    try:
        doc_ref = create_document_reference_service(db, body, current_user.id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=404, detail="Project not found") from e
    except TokenNotFoundError as e:
        raise HTTPException(status_code=404, detail="Token not found") from e
    return _to_read(db, doc_ref)


@router.get("/{doc_ref_id}", response_model=DocumentReferenceRead)
def get_document_reference(
    doc_ref_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentReferenceRead:
    doc_ref = get_document_reference_service(db, doc_ref_id)
    if not doc_ref:
        raise HTTPException(status_code=404, detail="Document reference not found")
    return _to_read(db, doc_ref)


@router.patch("/{doc_ref_id}", response_model=DocumentReferenceRead)
def update_document_reference(
    doc_ref_id: uuid.UUID,
    body: DocumentReferenceUpdate,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentReferenceRead:
    doc_ref = update_document_reference_service(db, doc_ref_id, body, current_user.id)
    if not doc_ref:
        raise HTTPException(status_code=404, detail="Document reference not found")
    return _to_read(db, doc_ref)


@router.delete("/{doc_ref_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_reference(
    doc_ref_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = soft_delete_document_reference_service(db, doc_ref_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Document reference not found")
