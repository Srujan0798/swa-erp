VALID_TRANSITIONS = {
    "todo": ["in_progress"],
    "in_progress": ["todo", "done"],
    "done": ["in_progress"],
}


def validate_transition(current_status: str, new_status: str) -> bool:
    valid = VALID_TRANSITIONS.get(current_status, [])
    if new_status not in valid:
        raise ValueError(
            f"Invalid transition from '{current_status}' to '{new_status}'. "
            f"Valid transitions: {valid}"
        )
    return True


def get_valid_transitions(current_status: str) -> list[str]:
    return VALID_TRANSITIONS.get(current_status, [])
