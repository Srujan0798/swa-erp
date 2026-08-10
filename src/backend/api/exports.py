import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from src.backend.core.deps import require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User
from src.backend.services.export_service import (
    export_demo_package,
    export_financial_report,
    export_project_slides,
    export_project_summary,
)
from src.backend.workers.tasks import generate_project_summary_pdf

router = APIRouter(prefix="/api/exports", tags=["exports"])


@router.get("/projects/{project_id}/summary.pdf")
def project_summary_pdf(
    project_id: uuid.UUID,
    async_: bool = Query(False, alias="async", description="Enqueue as background job"),
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    if async_:
        task = generate_project_summary_pdf.delay(str(project_id))
        return Response(
            content=f'{{"job_id": "{task.id}"}}',
            media_type="application/json",
            status_code=202,
        )

    try:
        pdf_bytes = export_project_summary(db, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    filename = f"project-summary-{project_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/reports/financial.pdf")
def financial_report_pdf(
    start_date: date = Query(..., description="Report start date"),  # noqa: B008
    end_date: date = Query(..., description="Report end date"),  # noqa: B008
    async_: bool = Query(False, alias="async", description="Enqueue as background job"),
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")
    if async_:
        from src.backend.workers.tasks import generate_financial_report_pdf

        task = generate_financial_report_pdf.delay(
            start_date.isoformat(), end_date.isoformat()
        )
        return Response(
            content=f'{{"job_id": "{task.id}"}}',
            media_type="application/json",
            status_code=202,
        )

    pdf_bytes = export_financial_report(db, start_date, end_date)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="financial-report.pdf"'},
    )


@router.get("/projects/{project_id}/slides.pdf")
def project_slides_pdf(
    project_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Response:
    try:
        pdf_bytes = export_project_slides(db, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    filename = f"project-slides-{project_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/projects/{project_id}/demo.json")
def demo_package_json(
    project_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.PM)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Response:
    try:
        data = export_demo_package(db, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    import json

    return Response(
        content=json.dumps(data, default=str),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="demo-package-{project_id}.json"'},
    )
