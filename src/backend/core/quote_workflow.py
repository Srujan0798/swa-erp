VALID_TRANSITIONS = {
    "draft": ["pending_approval"],
    "pending_approval": ["approved", "draft"],
    "approved": ["sent", "draft"],
    "sent": ["accepted", "rejected"],
    "rejected": ["draft"],
    "accepted": [],
}


def can_transition(from_status: str, to_status: str) -> bool:
    return to_status in VALID_TRANSITIONS.get(from_status, [])


def get_allowed_transitions(status: str) -> list[str]:
    return VALID_TRANSITIONS.get(status, [])
