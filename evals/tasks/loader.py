"""
evals/tasks/loader.py — loads task YAML specs for reference/validation.

The actual eval logic lives in evals/wave_43_evals.py (as pytest tests that
mirror the task specs). This loader is used by the GitHub Actions workflow
and by tools that need to enumerate the task catalog programmatically.
"""
import yaml
from pathlib import Path

TASKS_DIR = Path(__file__).resolve().parent

def load_tasks() -> list[dict]:
    """Load all .task.yaml files from evals/tasks/."""
    tasks = []
    for f in sorted(TASKS_DIR.glob("*.task.yaml")):
        with open(f) as fh:
            t = yaml.safe_load(fh)
            t["_file"] = str(f)
            tasks.append(t)
    return tasks

def task_by_id(task_id: str) -> dict | None:
    """Look up a task by its id prefix."""
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id or t["id"].startswith(task_id):
            return t
    return None
