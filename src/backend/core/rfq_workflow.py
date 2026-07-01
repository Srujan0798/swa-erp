VALID_TRANSITIONS = {
    "draft": ["sent", "cancelled"],
    "sent": ["responded", "cancelled"],
    "responded": ["compared", "closed"],
    "compared": ["awarded", "closed"],
    "awarded": ["closed"],
    "closed": [],
    "cancelled": [],
}


def can_transition(from_status: str, to_status: str) -> bool:
    return to_status in VALID_TRANSITIONS.get(from_status, [])


def get_allowed_transitions(status: str) -> list[str]:
    return VALID_TRANSITIONS.get(status, [])
