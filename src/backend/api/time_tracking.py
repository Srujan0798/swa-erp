import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.backend.core.deps import get_current_user, require_role
from src.backend.core.roles import Role
from src.backend.db.session import get_db
from src.backend.models.user import User


def _is_admin(user: User) -> bool:
    return user.role == Role.ADMIN.value


def _scoped_user_id(current_user: User, requested: uuid.UUID | None) -> uuid.UUID | None:
    """Meeting 1: time log is owner-only; Admin may see all / filter any user."""
    if _is_admin(current_user):
        return requested
    if requested is not None and requested != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot view another user's time data")
    return current_user.id
from src.backend.schemas.time_tracking import (
    TimeEntryCreate,
    TimeEntryListResponse,
    TimeEntryRead,
    TimeEntryUpdate,
    TimesheetListResponse,
    TimesheetRead,
)
from src.backend.services.time_service import (
    approve_timesheet_service,
    create_time_entry_service,
    delete_time_entry_service,
    generate_timesheet_service,
    get_timesheet_service,
    list_time_entries_service,
    list_timesheets_service,
    reject_timesheet_service,
    submit_timesheet_service,
    update_time_entry_service,
)

time_entries_router = APIRouter(prefix="/api/time-entries", tags=["time-entries"])
timesheets_router = APIRouter(prefix="/api/timesheets", tags=["timesheets"])


@time_entries_router.post("", response_model=TimeEntryRead, status_code=status.HTTP_201_CREATED)
def create_time_entry(
    body: TimeEntryCreate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TimeEntryRead:
    return create_time_entry_service(db, current_user.id, body)


@time_entries_router.get("", response_model=TimeEntryListResponse)
def list_time_entries(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    project_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> TimeEntryListResponse:
    return list_time_entries_service(
        db,
        project_id=project_id,
        user_id=_scoped_user_id(current_user, user_id),
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


@time_entries_router.get("/{entry_id}", response_model=TimeEntryRead)
def get_time_entry(
    entry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TimeEntryRead:
    from src.backend.db.repositories.time_repo import get_time_entry_by_id
    from src.backend.services.time_service import _entry_to_read

    entry = get_time_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    if not _is_admin(current_user) and entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot view another user's time data")
    return _entry_to_read(entry, db)


@time_entries_router.patch("/{entry_id}", response_model=TimeEntryRead)
def update_time_entry(
    entry_id: uuid.UUID,
    body: TimeEntryUpdate,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TimeEntryRead:
    return update_time_entry_service(db, entry_id, current_user.id, body)


@time_entries_router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_entry(
    entry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    delete_time_entry_service(db, entry_id, current_user.id)


@timesheets_router.get("", response_model=TimesheetListResponse)
def list_timesheets(
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
    user_id: uuid.UUID | None = None,
    ts_status: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> TimesheetListResponse:
    return list_timesheets_service(
        db,
        user_id=_scoped_user_id(current_user, user_id),
        status=ts_status,
        page=page,
        page_size=page_size,
    )


@timesheets_router.get("/{timesheet_id}", response_model=TimesheetRead)
def get_timesheet(
    timesheet_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TimesheetRead:
    result = get_timesheet_service(db, timesheet_id)
    if not result:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    if not _is_admin(current_user) and result.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot view another user's timesheet")
    return result


@timesheets_router.post("/generate", response_model=TimesheetRead)
def generate_timesheet(
    week_start: date,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TimesheetRead:
    return generate_timesheet_service(db, current_user.id, week_start)


@timesheets_router.post("/{timesheet_id}/submit", response_model=TimesheetRead)
def submit_timesheet(
    timesheet_id: uuid.UUID,
    current_user: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TimesheetRead:
    return submit_timesheet_service(db, timesheet_id, current_user.id)


@timesheets_router.post("/{timesheet_id}/approve", response_model=TimesheetRead)
def approve_timesheet(
    timesheet_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TimesheetRead:
    return approve_timesheet_service(db, timesheet_id, current_user.id)


@timesheets_router.post("/{timesheet_id}/reject", response_model=TimesheetRead)
def reject_timesheet(
    timesheet_id: uuid.UUID,
    current_user: User = Depends(require_role(Role.ADMIN)),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> TimesheetRead:
    return reject_timesheet_service(db, timesheet_id, current_user.id)
