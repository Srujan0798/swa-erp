from enum import StrEnum


class ProjectStatus(StrEnum):
    LEAD = "Lead"
    QUOTE = "Quote"
    AWARDED = "Awarded"
    DESIGN = "Design"
    VENDOR = "Vendor"
    EXECUTION = "Execution"
    VALIDATION = "Validation"
    CLOSED = "Closed"


ALLOWED_TRANSITIONS = {
    ProjectStatus.LEAD: {ProjectStatus.QUOTE},
    ProjectStatus.QUOTE: {ProjectStatus.LEAD, ProjectStatus.AWARDED},
    ProjectStatus.AWARDED: {ProjectStatus.DESIGN, ProjectStatus.QUOTE},
    ProjectStatus.DESIGN: {ProjectStatus.VENDOR, ProjectStatus.AWARDED},
    ProjectStatus.VENDOR: {ProjectStatus.EXECUTION, ProjectStatus.DESIGN},
    ProjectStatus.EXECUTION: {ProjectStatus.VALIDATION, ProjectStatus.VENDOR},
    ProjectStatus.VALIDATION: {ProjectStatus.CLOSED, ProjectStatus.EXECUTION},
    ProjectStatus.CLOSED: set(),
}


def can_transition(from_status: ProjectStatus, to_status: ProjectStatus) -> bool:
    return to_status in ALLOWED_TRANSITIONS.get(from_status, set())
