"""Generate synthetic .xlsx fixtures for the Wave 13 import tests.

These contain NO real client data — only fabricated rows that exercise the
header-detection + mapping logic. Run: python3 tests/wave-13/generate_fixtures.py
"""
from __future__ import annotations

from pathlib import Path

import openpyxl

HERE = Path(__file__).parent
FIX = HERE / "fixtures"
FIX.mkdir(exist_ok=True)


def _save(name: str, header: list[str], rows: list[list]) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header)
    for r in rows:
        ws.append(r)
    wb.save(FIX / name)


def main() -> None:
    _save(
        "clients_sample.xlsx",
        ["Columns", "Sr No", "Client ID", "Client Name", "Industry", "Date Onboarded",
         "Primary Contact", "Email", "Phone", "Billing Address", "Client Status",
         "First Lead ID", "First Inquiry ID", "Notes"],
        [["", 1, "SWA-2025-CLT-002", "Beta LLC", "Construction", "", "",
          "beta@example.com", "9999999999", "123 St", "Active", "LDI-001",
          "SWA-2025-INQ-001", "note"]],
    )
    _save(
        "inquiries_sample.xlsx",
        ["Sr No", "Inquiry ID", "Inquiry Date", "Inquiry Type", "Inquiry Source",
         "Client Name", "Requirement Summary", "Estimated Value", "Priority",
         "Status", "Owner", "Technical Lead", "Notes"],
        [[1, "SWA-2025-INQ-002", "2025-02-01", "Design", "Referral", "Acme Corp",
          "Need design", "100000", "High", "New", "", "", "note"]],
    )
    _save(
        "agreements_sample.xlsx",
        ["Columns", "Sr No", "Agreement ID", "Client Name", "Client ID", "Inquiry ID",
         "Service Name", "Start Date", "End Date", "Total Tokens", "Status", "Notes"],
        [["", 1, "SWA-2025-SA-012", "Acme Corp", "SWA-2025-CLT-001", "SWA-2025-INQ-001",
          "INSUDESIGN", "2025-10-01 00:00:00", "2026-03-31 00:00:00", "10", "Active", "Monthly"]],
    )
    _save(
        "tokens_sample.xlsx",
        ["Columns", "Sr. No.", "Date", "Token ID", "Agreement ID", "Token Type",
         "Description", "Token Status", "Tokens Used", "Swa Employee Name/Team Leader",
         "Project Owner", "Client Employee Name"],
        [["", 1, "2025-10-03 00:00:00", "SWA-2025-TKN-001", "SWA-2025-SA-011", "Query",
          "System R & U value calculation", "In Progress", "1", "Mihir", "", "Akash"]],
    )
    _save(
        "document_references_sample.xlsx",
        ["", "Sr. No.", "Date", "Doc Ref No", "Associated Project/Token ID", "Author",
         "Document Type", "Type", "User", "Description", "Revision", "Status", "Remarks"],
        [["", 1, "2024-01-15 00:00:00", "SWA-2025-DRN-001", "SWA-2025-PRJ-065", "Full Name",
          "Concept Note", "Submittal", "John Smith", "Concept note desc", "R0", "Issued", "ok"]],
    )
    _save(
        "projects_sample.xlsx",
        ["", "Sr. No.", "Project ID", "Client ID", "Inquiry ID", "Client Name",
         "Project Name", "Start date", "End date", "Milestone", "Progress Indicators",
         "Status Updates", "Team Leader", "Project owner", "Notes"],
        [["", 1, "SWA-2025-PRJ-066", "SWA-2025-CLT-001", "SWA-2025-INQ-001", "Acme Corp",
          "Riverfront", "2025-01-01", "2025-06-01", "", "", "Lead", "Mihir", "Sita", "note"]],
    )
    _save(
        "time_logs_sample.xlsx",
        ["Column", "Sr. No.", "Date", "Employee Name", "Employee Role", "Work Type",
         "Reference ID", "Revision", "Project Name", "Activity Type", "Software Used",
         "Work Mode", "Hours Logged", "Billable Hours", "Remarks (optional)"],
        [["", 1, "2025-03-01", "Mihir", "Engineer", "Design", "SWA-2025-PRJ-065", "No",
          "Green Tower", "Drafting", "AutoCAD", "Manual", "2", "2", "ok"]],
    )
    _save(
        "sustainability_sample.xlsx",
        ["Columns", "Sr No", "Date", "Reference ID", "Compliant with Green Standards",
         "Total Energy Saved (kWh)", "CO2 emissions avoided (tCO2e)",
         "Lifecycle Cost savings delivered (INR)", "Insulation Efficiency (Actual / Expected)",
         "Payback Period (Months)", "Notes"],
        [["", 1, "2025-04-01", "SWA-2025-PRJ-065", "No", "1200", "3.5", "50000", "0.89",
          "24", "annual"]],
    )
    print(f"fixtures written to {FIX}")


if __name__ == "__main__":
    main()
