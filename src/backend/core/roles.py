from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    PM = "pm"
    DESIGNER = "designer"
    AUDITOR = "auditor"
    VIEWER = "viewer"


ROLE_HIERARCHY = {
    Role.ADMIN: {Role.ADMIN, Role.PM, Role.DESIGNER, Role.AUDITOR, Role.VIEWER},
    Role.PM: {Role.PM, Role.DESIGNER, Role.AUDITOR, Role.VIEWER},
    Role.DESIGNER: {Role.DESIGNER, Role.VIEWER},
    Role.AUDITOR: {Role.AUDITOR, Role.VIEWER},
    Role.VIEWER: {Role.VIEWER},
}


def role_includes(user_role: Role, required: Role) -> bool:
    return required in ROLE_HIERARCHY.get(user_role, set())
