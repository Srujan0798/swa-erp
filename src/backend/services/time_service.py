import uuid
from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.backend.db.repositories.project_repo import get_by_id as get_project_by_id
from src.backend.db.repositories.time_repo import (
    create_or_update_timesheet,
    create_time_entry,
    get_time_entry_by_id,
    get_timesheet_by_id,
    get_timesheet_by_user_week,
    list_time_entries,
    list_timesheets,
    list_user_entries_for_week,
    soft_delete_time_entry,
    update_time_entry,
)
from src.backend.db.repositories.user_repo import get_by_id as get_user_by_id
from src.backend.schemas.time_tracking import (
    TimeEntryCreate,
    TimeEntryListResponse,
    TimeEntryRead,
    TimeEntryUpdate,
    TimesheetListResponse,
    TimesheetRead,
    TimesheetStatus,
)


def _validate_hours(hours: Decimal) -> None:
    if hours % Decimal("0.25") != 0:
        raise HTTPException(status_code=422, detail="Hours must be in 0.25 increments")
    if hours <= 0 or hours > 24:
        raise HTTPException(status_code=422, detail="Hours must be between 0 and 24")


def _get_week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _entry_to_read(entry, db: Session) -> TimeEntryRead:
    user = get_user_by_id(db, entry.user_id)
    project = get_project_by_id(db, entry.project_id)
    return TimeEntryRead(
        id=entry.id,
        project_id=entry.project_id,
        task_id=entry.task_id,
        user_id=entry.user_id,
        date=entry.date,
        hours=entry.hours,
        description=entry.description,
        is_billable=entry.is_billable,
        created_at=entry.created_at,
        user_name=user.name if user else None,
        project_name=project.name if project else None,
    )


def _timesheet_to_read(timesheet, db: Session, include_entries: bool = False) -> TimesheetRead:
    user = get_user_by_id(db, timesheet.user_id)
    approver = get_user_by_id(db, timesheet.approved_by) if timesheet.approved_by else None

    entries = []
    if include_entries:
        week_entries = list_user_entries_for_week(db, timesheet.user_id, timesheet.week_start)
        entries = [_entry_to_read(e, db) for e in week_entries]

    return TimesheetRead(
        id=timesheet.id,
        user_id=timesheet.user_id,
        week_start=timesheet.week_start,
        week_end=timesheet.week_end,
        status=TimesheetStatus(timesheet.status),
        total_hours=timesheet.total_hours,
        billable_hours=timesheet.billable_hours,
        approved_by=timesheet.approved_by,
        approved_at=timesheet.approved_at,
        created_at=timesheet.created_at,
        user_name=user.name if user else None,
        approved_by_name=approver.name if approver else None,
        entries=entries,
    )


def create_time_entry_service(
    db: Session,
    user_id: uuid.UUID,
    data: TimeEntryCreate,
) -> TimeEntryRead:
    _validate_hours(data.hours)

    project = get_project_by_id(db, data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    week_start = _get_week_start(data.date)
    ts = get_timesheet_by_user_week(db, user_id, week_start)
    if ts and ts.status == "approved":
        raise HTTPException(
            status_code=422, detail="Cannot add entry to an approved timesheet week"
        )

    entry = create_time_entry(db, {**data.model_dump(), "user_id": user_id})
    return _entry_to_read(entry, db)


def update_time_entry_service(
    db: Session,
    entry_id: uuid.UUID,
    user_id: uuid.UUID,
    data: TimeEntryUpdate,
) -> TimeEntryRead:
    entry = get_time_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    if entry.user_id != user_id:
        raise HTTPException(status_code=403, detail="Only the entry owner can update")

    week_start = _get_week_start(entry.date)
    ts = get_timesheet_by_user_week(db, entry.user_id, week_start)
    if ts and ts.status == "approved":
        raise HTTPException(
            status_code=422, detail="Cannot edit entry in an approved timesheet week"
        )

    update_data = data.model_dump(exclude_unset=True)
    if "hours" in update_data:
        _validate_hours(update_data["hours"])

    updated = update_time_entry(db, entry_id, update_data)
    return _entry_to_read(updated, db)


def delete_time_entry_service(
    db: Session,
    entry_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    entry = get_time_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    if entry.user_id != user_id:
        raise HTTPException(status_code=403, detail="Only the entry owner can delete")

    week_start = _get_week_start(entry.date)
    ts = get_timesheet_by_user_week(db, entry.user_id, week_start)
    if ts and ts.status == "approved":
        raise HTTPException(
            status_code=422, detail="Cannot delete entry in an approved timesheet week"
        )

    return soft_delete_time_entry(db, entry_id)


def list_time_entries_service(
    db: Session,
    project_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> TimeEntryListResponse:
    items, total, pg, ps = list_time_entries(
        db,
        project_id=project_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return TimeEntryListResponse(
        items=[_entry_to_read(e, db) for e in items],
        total=total,
        page=pg,
        page_size=ps,
    )


def generate_timesheet_service(
    db: Session,
    user_id: uuid.UUID,
    week_start: date,
) -> TimesheetRead:
    week_start = _get_week_start(week_start)
    entries = list_user_entries_for_week(db, user_id, week_start)
    timesheet = create_or_update_timesheet(db, user_id, week_start, entries)
    return _timesheet_to_read(timesheet, db, include_entries=True)


def _create_audit_log(db: Session, timesheet_id: uuid.UUID, action: str, performed_by: uuid.UUID):
    from src.backend.models.time_tracking import TimesheetAuditLog

    log = TimesheetAuditLog(
        timesheet_id=timesheet_id,
        action=action,
        performed_by=performed_by,
    )
    db.add(log)


def submit_timesheet_service(
    db: Session,
    timesheet_id: uuid.UUID,
    user_id: uuid.UUID,
) -> TimesheetRead:
    ts = get_timesheet_by_id(db, timesheet_id)
    if not ts:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    if ts.user_id != user_id:
        raise HTTPException(status_code=403, detail="Only the owner can submit")
    if ts.status != "draft":
        raise HTTPException(status_code=422, detail="Only draft timesheets can be submitted")

    ts.status = "submitted"
    _create_audit_log(db, timesheet_id, "submitted", user_id)
    db.commit()
    db.refresh(ts)
    return _timesheet_to_read(ts, db, include_entries=True)


def approve_timesheet_service(
    db: Session,
    timesheet_id: uuid.UUID,
    manager_id: uuid.UUID,
) -> TimesheetRead:
    ts = get_timesheet_by_id(db, timesheet_id)
    if not ts:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    if ts.status != "submitted":
        raise HTTPException(status_code=422, detail="Only submitted timesheets can be approved")

    ts.status = "approved"
    ts.approved_by = manager_id
    from datetime import datetime as _dt
    from datetime import timezone as _tz

    ts.approved_at = _dt.now(_tz.utc)
    _create_audit_log(db, timesheet_id, "approved", manager_id)
    db.commit()
    db.refresh(ts)
    return _timesheet_to_read(ts, db, include_entries=True)


def reject_timesheet_service(
    db: Session,
    timesheet_id: uuid.UUID,
    manager_id: uuid.UUID,
) -> TimesheetRead:
    ts = get_timesheet_by_id(db, timesheet_id)
    if not ts:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    if ts.status != "submitted":
        raise HTTPException(status_code=422, detail="Only submitted timesheets can be rejected")

    ts.status = "rejected"
    ts.approved_by = manager_id
    from datetime import datetime as _dt
    from datetime import timezone as _tz

    ts.approved_at = _dt.now(_tz.utc)
    _create_audit_log(db, timesheet_id, "rejected", manager_id)
    db.commit()
    db.refresh(ts)
    return _timesheet_to_read(ts, db, include_entries=True)


def list_timesheets_service(
    db: Session,
    user_id: uuid.UUID | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> TimesheetListResponse:
    items, total, pg, ps = list_timesheets(
        db, user_id=user_id, status=status, page=page, page_size=page_size
    )
    return TimesheetListResponse(
        items=[_timesheet_to_read(t, db) for t in items],
        total=total,
        page=pg,
        page_size=ps,
    )


def get_timesheet_service(
    db: Session,
    timesheet_id: uuid.UUID,
) -> TimesheetRead | None:
    ts = get_timesheet_by_id(db, timesheet_id)
    if not ts:
        return None
    return _timesheet_to_read(ts, db, include_entries=True)
