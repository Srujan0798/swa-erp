import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role, role_includes
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.schemas.document_reference import (
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

router = APIRouter(prefix="/api/document-references", tags=["document-references"])


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
        items=[DocumentReferenceRead.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
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
        allowed = {Role.PM, Role.DESIGNER}
    elif doc_type == "REFORGE":
        allowed = {Role.AUDITOR, Role.DESIGNER}
    else:
        allowed = {Role.PM}
    if not any(role_includes(Role(current_user.role), r) for r in allowed):
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
    return DocumentReferenceRead.model_validate(doc_ref)


@router.get("/{doc_ref_id}", response_model=DocumentReferenceRead)
def get_document_reference(
    doc_ref_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> DocumentReferenceRead:
    doc_ref = get_document_reference_service(db, doc_ref_id)
    if not doc_ref:
        raise HTTPException(status_code=404, detail="Document reference not found")
    return DocumentReferenceRead.model_validate(doc_ref)


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
    return DocumentReferenceRead.model_validate(doc_ref)


@router.delete("/{doc_ref_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_reference(
    doc_ref_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    success = soft_delete_document_reference_service(db, doc_ref_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Document reference not found")
