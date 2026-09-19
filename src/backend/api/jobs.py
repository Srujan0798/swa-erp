import uuid

from celery.result import AsyncResult  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from src.backend.core.deps import require_role
from src.backend.core.roles import Role, role_includes
from src.backend.core.storage import get_storage
from src.backend.db.repositories.project_repo import user_has_project_access
from src.backend.db.session import get_db
from src.backend.models.export_job import ExportJob
from src.backend.models.user import User
from src.backend.workers.celery_app import app as celery_app

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

get_current_pm = Depends(require_role(Role.PM))


def _require_job_owner(db: Session, job_id: str, user: User) -> None:
    """Raise 404 unless *user* enqueued *job_id* (SEC-07).

    Admins bypass the ownership check (explicit product call: admins may read
    any job). On mismatch we return 404, NOT 403 — a 403 would confirm the
    job id exists, which is itself a small leak.

    Unknown job IDs are rejected with 404 to prevent enumeration.
    """
    if role_includes(Role(user.role), Role.ADMIN):
        return  # admins may read any job
    owner = db.get(ExportJob, job_id)
    if owner is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if owner.user_id != user.id:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")


def _require_project_access(
    db: Session,
    project_id: uuid.UUID,
    user: User,
) -> None:
    """Raise 403 when *user* does not belong to *project_id*."""
    if not user_has_project_access(db, user.id, project_id):
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this project's jobs",
        )


@router.get("/{job_id}")
def get_job_status(
    job_id: str,
    current_user: User = get_current_pm,
    db: Session = Depends(get_db),  # noqa: B008
) -> dict:
    _require_job_owner(db, job_id, current_user)
    result = AsyncResult(job_id, app=celery_app)
    response: dict = {"job_id": job_id, "status": result.state.lower()}

    if result.state == "PENDING":
        pass
    elif result.state == "STARTED":
        pass
    elif result.state == "SUCCESS":
        response["result_url"] = get_storage().url(result.result)
    elif result.state == "FAILURE":
        response["error"] = str(result.result)
    return response


@router.get("/{job_id}/result")
def get_job_result(
    job_id: str,
    current_user: User = get_current_pm,
    db: Session = Depends(get_db),  # noqa: B008
) -> Response:
    _require_job_owner(db, job_id, current_user)
    result = AsyncResult(job_id, app=celery_app)
    if result.state != "SUCCESS":
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} has no downloadable result (state: {result.state})",
        )

    result_key = result.result
    if not isinstance(result_key, str):
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} result is not a stored file",
        )

    try:
        content = get_storage().read(result_key)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} result file is no longer available",
        ) from None

    filename = result_key.split("/")[-1]
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
