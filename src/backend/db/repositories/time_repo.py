import uuid
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.backend.models.time_tracking import TimeEntry, Timesheet


def create_time_entry(db: Session, data: dict[str, Any]) -> TimeEntry:
    entry = TimeEntry(**data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_time_entry_by_id(db: Session, entry_id: uuid.UUID) -> TimeEntry | None:
    return (
        db.query(TimeEntry)
        .filter(
            TimeEntry.id == entry_id,
            TimeEntry.deleted_at.is_(None),
        )
        .first()
    )


def update_time_entry(db: Session, entry_id: uuid.UUID, data: dict[str, Any]) -> TimeEntry | None:
    entry = get_time_entry_by_id(db, entry_id)
    if not entry:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry


def soft_delete_time_entry(db: Session, entry_id: uuid.UUID) -> bool:
    entry = get_time_entry_by_id(db, entry_id)
    if not entry:
        return False
    entry.deleted_at = datetime.now(tz=UTC)
    db.commit()
    return True


def list_time_entries(
    db: Session,
    project_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[TimeEntry], int, int, int]:
    query = db.query(TimeEntry).filter(TimeEntry.deleted_at.is_(None))

    if project_id:
        query = query.filter(TimeEntry.project_id == project_id)
    if user_id:
        query = query.filter(TimeEntry.user_id == user_id)
    if start_date:
        query = query.filter(TimeEntry.date >= start_date)
    if end_date:
        query = query.filter(TimeEntry.date <= end_date)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(TimeEntry.date.desc()).offset(offset).limit(page_size).all()

    return items, total, page, page_size


def list_user_entries_for_week(
    db: Session, user_id: uuid.UUID, week_start: date
) -> list[TimeEntry]:
    from datetime import timedelta

    week_end = week_start + timedelta(days=6)
    return (
        db.query(TimeEntry)
        .filter(
            TimeEntry.user_id == user_id,
            TimeEntry.date >= week_start,
            TimeEntry.date <= week_end,
            TimeEntry.deleted_at.is_(None),
        )
        .all()
    )


def get_timesheet_by_id(db: Session, timesheet_id: uuid.UUID) -> Timesheet | None:
    return db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()


def get_timesheet_by_user_week(
    db: Session, user_id: uuid.UUID, week_start: date
) -> Timesheet | None:
    return (
        db.query(Timesheet)
        .filter(
            Timesheet.user_id == user_id,
            Timesheet.week_start == week_start,
        )
        .first()
    )


def create_or_update_timesheet(
    db: Session,
    user_id: uuid.UUID,
    week_start: date,
    entries: list[TimeEntry],
) -> Timesheet:
    from datetime import timedelta

    week_end = week_start + timedelta(days=6)
    total_hours = sum(e.hours for e in entries)
    billable_hours = sum(e.hours for e in entries if e.is_billable)

    timesheet = get_timesheet_by_user_week(db, user_id, week_start)
    if timesheet:
        timesheet.total_hours = total_hours
        timesheet.billable_hours = billable_hours
        timesheet.week_end = week_end
    else:
        timesheet = Timesheet(
            user_id=user_id,
            week_start=week_start,
            week_end=week_end,
            total_hours=total_hours,
            billable_hours=billable_hours,
        )
        db.add(timesheet)

    db.commit()
    db.refresh(timesheet)
    return timesheet


def list_timesheets(
    db: Session,
    user_id: uuid.UUID | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Timesheet], int, int, int]:
    query = db.query(Timesheet)

    if user_id:
        query = query.filter(Timesheet.user_id == user_id)
    if status:
        query = query.filter(Timesheet.status == status)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Timesheet.week_start.desc()).offset(offset).limit(page_size).all()

    return items, total, page, page_size
