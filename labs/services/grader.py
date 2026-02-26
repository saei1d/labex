import subprocess
from labs.models import TaskValidationRule


class GradingException(Exception):
    pass


def _sanitize_feedback(raw: str) -> str:
    sanitized = raw.replace("AssertionError", "ValidationError")
    return sanitized[:400]


def evaluate_task(session, task):
    rules = TaskValidationRule.objects.filter(task=task)
    if not rules.exists():
        return False, "Validation rule is not configured"

    for rule in rules:
        config = rule.config_json or {}
        command = config.get("command")
        if not command:
            return False, "Validator configuration is invalid"

        proc = subprocess.run(
            ["docker", "exec", session.container_id, "sh", "-lc", command],
            capture_output=True,
            text=True,
            timeout=rule.timeout_seconds,
        )
        if proc.returncode != 0:
            feedback = _sanitize_feedback(proc.stderr or proc.stdout or "Task validation failed")
            return False, feedback

    return True, "Task passed successfully"
