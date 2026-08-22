import uuid
from collections import defaultdict
from datetime import date
from decimal import Decimal

from fpdf import FPDF  # type: ignore[import-untyped]
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.backend.db.repositories.client_repo import get_by_id as get_client_by_id
from src.backend.db.repositories.project_repo import get_by_id as get_project_by_id
from src.backend.db.repositories.task_repo import get_task_counts_by_project, list_by_project
from src.backend.db.repositories.time_repo import list_time_entries
from src.backend.db.repositories.user_repo import get_by_id as get_user_by_id
from src.backend.models.boq import BOQItem
from src.backend.models.project_cost import ProjectCost
from src.backend.models.quote import Quote
from src.backend.services.project_pnl_service import get_default_hourly_rate


class _SWAPdf(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, "SWA Consultancy Pvt. Ltd.", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_draw_color(100, 100, 100)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def _section_title(self, title: str) -> None:
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)

    def _kv_row(self, label: str, value: str, label_w: int = 50, val_w: int = 130) -> None:
        self.set_font("Helvetica", "B", 10)
        self.cell(label_w, 7, label)
        self.set_font("Helvetica", "", 10)
        self.cell(val_w, 7, value, new_x="LMARGIN", new_y="NEXT")

    def _table_header(self, headers: list[str], widths: list[int]) -> None:
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(200, 200, 200)
        for i, h in enumerate(headers):
            self.cell(widths[i], 7, h, border=1, fill=True, align="C")
        self.ln()

    def _table_row(
        self, values: list[str], widths: list[int], aligns: list[str] | None = None
    ) -> None:
        self.set_font("Helvetica", "", 8)
        if aligns is None:
            aligns = ["L"] * len(values)
        for i, val in enumerate(values):
            self.cell(widths[i], 6, val, border=1, align=aligns[i])
        self.ln()


def _safe_str(val: object | None, fallback: str = "N/A") -> str:
    if val is None:
        return fallback
    return str(val)


def _fmt_decimal(val: Decimal | float | str | None, fallback: str = "0.00") -> str:
    if val is None:
        return fallback
    return f"{Decimal(str(val)):,.2f}"


def _fmt_date(val: date | None, fallback: str = "N/A") -> str:
    if val is None:
        return fallback
    return val.strftime("%d %b %Y")


def export_project_summary(db: Session, project_id: uuid.UUID) -> bytes:
    project = get_project_by_id(db, project_id)
    if not project:
        raise ValueError("Project not found")

    client = get_client_by_id(db, project.client_id) if project.client_id else None
    pm = get_user_by_id(db, project.pm_id) if project.pm_id else None
    designer = get_user_by_id(db, project.designer_id) if project.designer_id else None
    auditor = get_user_by_id(db, project.auditor_id) if project.auditor_id else None

    boq_items = (
        db.query(BOQItem).join(BOQItem.boq).filter(BOQItem.boq.has(project_id=project_id)).all()
    )
    boq_total = sum((item.amount for item in boq_items), Decimal("0"))
    boq_count = len(boq_items)

    task_counts = get_task_counts_by_project(db, project_id)
    tasks_total = sum(task_counts.values())

    team = []
    if pm:
        team.append(("Project Manager", pm.name))
    if designer:
        team.append(("Designer", designer.name))
    if auditor:
        team.append(("Auditor", auditor.name))

    pdf = _SWAPdf()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf._section_title("Project Information")
    pdf._kv_row("Project Name:", _safe_str(project.name))
    pdf._kv_row("Project Code:", _safe_str(project.code))
    pdf._kv_row("Client:", _safe_str(client.name if client else None))
    pdf._kv_row("Status:", project.status.replace("_", " ").title())
    pdf._kv_row("Location:", _safe_str(project.location))
    pdf._kv_row("Start Date:", _fmt_date(project.start_date))
    pdf._kv_row("Target End:", _fmt_date(project.target_end_date))
    pdf._kv_row("Estimated Value:", _fmt_decimal(project.estimated_value))
    pdf._kv_row("Actual Value:", _fmt_decimal(project.actual_value))
    pdf.ln(4)

    pdf._section_title("BOQ Summary")
    pdf._kv_row("Total BOQ Value:", _fmt_decimal(boq_total))
    pdf._kv_row("Item Count:", str(boq_count))
    pdf.ln(4)

    pdf._section_title("Task Status Breakdown")
    pdf._table_header(["Status", "Count"], [60, 40])
    for status_key in ("todo", "in_progress", "done"):
        count = task_counts.get(status_key, 0)
        label = status_key.replace("_", " ").title()
        pdf._table_row([label, str(count)], [60, 40], ["L", "R"])
    pdf._table_row(["Total", str(tasks_total)], [60, 40], ["L", "R"])
    pdf.ln(4)

    if team:
        pdf._section_title("Team Members")
        pdf._table_header(["Role", "Name"], [60, 120])
        for role, name in team:
            pdf._table_row([role, name], [60, 120])
    pdf.ln(4)

    return bytes(pdf.output())


def export_financial_report(db: Session, start_date: date, end_date: date) -> bytes:
    from datetime import timedelta

    time_entries, _, _, _ = list_time_entries(
        db, start_date=start_date, end_date=end_date, page=1, page_size=10000
    )

    monthly_hours: dict[str, Decimal] = defaultdict(Decimal)
    billable_hours: dict[str, Decimal] = defaultdict(Decimal)
    for entry in time_entries:
        month_key = entry.date.strftime("%Y-%m")
        monthly_hours[month_key] += entry.hours
        if entry.is_billable:
            billable_hours[month_key] += entry.hours

    quotes = (
        db.query(Quote)
        .filter(
            Quote.deleted_at.is_(None),
            Quote.created_at >= start_date,
            Quote.created_at <= end_date + timedelta(days=1),
        )
        .all()
    )

    accepted = [q for q in quotes if q.client_response == "accepted"]
    pending = [q for q in quotes if q.status in ("sent", "pending_approval")]
    total_revenue = sum((q.total_amount for q in accepted), Decimal("0"))
    total_pending = sum((q.total_amount for q in pending), Decimal("0"))

    pdf = _SWAPdf()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf._section_title("Financial Report")
    pdf._kv_row("Period:", f"{_fmt_date(start_date)} - {_fmt_date(end_date)}")
    pdf._kv_row("Generated:", _fmt_date(date.today(), fallback="Today"))
    pdf.ln(4)

    pdf._section_title("Time Summary")
    pdf._kv_row("Total Hours Logged:", f"{sum(monthly_hours.values()):.1f}")
    pdf._kv_row("Billable Hours:", f"{sum(billable_hours.values()):.1f}")
    pdf.ln(4)

    if monthly_hours:
        sorted_months = sorted(monthly_hours.keys())
        pdf._table_header(["Month", "Total Hours", "Billable Hours"], [50, 50, 50])
        for m in sorted_months:
            pdf._table_row(
                [m, f"{monthly_hours[m]:.1f}", f"{billable_hours[m]:.1f}"],
                [50, 50, 50],
                ["L", "R", "R"],
            )
        pdf.ln(4)

    pdf._section_title("Quote Revenue")
    pdf._kv_row("Quotes Generated:", str(len(quotes)))
    pdf._kv_row("Accepted Quotes:", str(len(accepted)))
    pdf._kv_row("Pending Quotes:", str(len(pending)))
    pdf._kv_row("Total Revenue (Accepted):", _fmt_decimal(total_revenue))
    pdf._kv_row("Pending Revenue:", _fmt_decimal(total_pending))
    pdf.ln(4)

    manual_costs = (
        db.query(func.coalesce(func.sum(ProjectCost.amount), 0))
        .filter(
            ProjectCost.deleted_at.is_(None),
            ProjectCost.date >= start_date,
            ProjectCost.date <= end_date,
        )
        .scalar()
    )
    time_cost = sum(billable_hours.values()) * get_default_hourly_rate()
    total_costs = Decimal(manual_costs) + time_cost
    net_pnl = total_revenue - total_costs

    pdf._section_title("Net Profit & Loss (Estimated)")
    pdf._kv_row("Revenue:", _fmt_decimal(total_revenue))
    pdf._kv_row("Estimated Costs:", _fmt_decimal(total_costs))
    pdf._kv_row("Net P&L:", _fmt_decimal(net_pnl))

    return bytes(pdf.output())


def export_project_slides(db: Session, project_id: uuid.UUID) -> bytes:
    project = get_project_by_id(db, project_id)
    if not project:
        raise ValueError("Project not found")

    client = get_client_by_id(db, project.client_id) if project.client_id else None
    task_counts = get_task_counts_by_project(db, project_id)
    tasks_total = sum(task_counts.values())
    done = task_counts.get("done", 0)

    est = Decimal(str(project.estimated_value)) if project.estimated_value else Decimal("0")
    act = Decimal(str(project.actual_value)) if project.actual_value else Decimal("0")
    budget_pct = f"{(act / est * 100):.0f}%" if est > 0 and act > 0 else "N/A"

    progress_pct = f"{(done / tasks_total * 100):.0f}%" if tasks_total > 0 else "0%"

    pdf = _SWAPdf()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=False)

    pdf.add_page(orientation="L")
    pdf.set_font("Helvetica", "B", 36)
    pdf.ln(60)
    pdf.cell(0, 20, _safe_str(project.name), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 18)
    pdf.cell(
        0,
        12,
        f"Project Status - {project.status.replace('_', ' ').title()}",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(
        0,
        10,
        f"Client: {_safe_str(client.name if client else None)}",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(0, 10, f"Date: {_fmt_date(date.today())}", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.add_page(orientation="L")
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, "Status Overview", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 16)
    pdf._kv_row("Status:", project.status.replace("_", " ").title(), 60, 200)
    pdf._kv_row("Location:", _safe_str(project.location), 60, 200)
    pdf._kv_row("Start Date:", _fmt_date(project.start_date), 60, 200)
    pdf._kv_row("Target End:", _fmt_date(project.target_end_date), 60, 200)
    pdf._kv_row("Completion:", progress_pct, 60, 200)

    pdf.add_page(orientation="L")
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, "Budget vs Actual", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 16)
    pdf._kv_row("Estimated:", _fmt_decimal(project.estimated_value), 60, 200)
    pdf._kv_row("Actual:", _fmt_decimal(project.actual_value), 60, 200)
    pdf._kv_row("Utilization:", budget_pct, 60, 200)

    pdf.add_page(orientation="L")
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, "Milestones", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 16)
    pdf._kv_row("Project Start:", _fmt_date(project.start_date), 60, 200)
    pdf._kv_row("Target Completion:", _fmt_date(project.target_end_date), 60, 200)
    pdf._kv_row("Actual Completion:", _fmt_date(project.actual_end_date, "Pending"), 60, 200)

    pdf.add_page(orientation="L")
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, "Next Steps", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 16)
    remaining = tasks_total - done
    pdf._kv_row("Tasks Remaining:", str(remaining), 60, 200)
    pdf._kv_row("Overall Progress:", progress_pct, 60, 200)
    if remaining > 0:
        pdf.ln(5)
        pdf.cell(
            0, 10, "Continue task execution and monitor milestones.", new_x="LMARGIN", new_y="NEXT"
        )
    else:
        pdf.ln(5)
        pdf.cell(
            0,
            10,
            "All tasks completed. Ready for validation and close-out.",
            new_x="LMARGIN",
            new_y="NEXT",
        )

    return bytes(pdf.output())


def export_demo_package(db: Session, project_id: uuid.UUID) -> dict:
    project = get_project_by_id(db, project_id)
    if not project:
        raise ValueError("Project not found")

    client = get_client_by_id(db, project.client_id) if project.client_id else None
    pm = get_user_by_id(db, project.pm_id) if project.pm_id else None
    designer = get_user_by_id(db, project.designer_id) if project.designer_id else None
    auditor = get_user_by_id(db, project.auditor_id) if project.auditor_id else None

    boq_items = (
        db.query(BOQItem)
        .join(BOQItem.boq)
        .filter(BOQItem.boq.has(project_id=project_id))
        .limit(10)
        .all()
    )

    tasks, _ = list_by_project(
        db, project_id, page=1, page_size=50, status=None, assignee_id=None, priority=None
    )

    team = []
    if pm:
        team.append({"role": "Project Manager", "name": pm.name})
    if designer:
        team.append({"role": "Designer", "name": designer.name})
    if auditor:
        team.append({"role": "Auditor", "name": auditor.name})

    return {
        "project": {
            "id": str(project.id),
            "name": project.name,
            "code": project.code,
            "description": project.description,
            "status": project.status,
            "location": project.location,
            "estimated_value": str(project.estimated_value) if project.estimated_value else None,
            "start_date": str(project.start_date) if project.start_date else None,
            "target_end_date": str(project.target_end_date) if project.target_end_date else None,
        },
        "client": {
            "name": client.name if client else None,
            "city": client.city if client else None,
        },
        "boq_items_sample": [
            {
                "line_number": item.line_number,
                "category": item.category,
                "description": item.description,
                "unit": item.unit,
                "quantity": str(item.quantity),
                "rate": str(item.rate),
                "amount": str(item.amount),
            }
            for item in boq_items
        ],
        "tasks": [
            {
                "id": str(task.id),
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "due_date": str(task.due_date) if task.due_date else None,
            }
            for task in tasks
        ],
        "team": team,
    }
