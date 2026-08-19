from celery.result import AsyncResult  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, HTTPException, Response

from src.backend.core.deps import require_role
from src.backend.core.roles import Role
from src.backend.core.storage import get_storage
from src.backend.models.user import User
from src.backend.workers.celery_app import app

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}")
def get_job_status(
    job_id: str,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
) -> dict:
    result = AsyncResult(job_id, app=app)
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
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
) -> Response:
    result = AsyncResult(job_id, app=app)
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
