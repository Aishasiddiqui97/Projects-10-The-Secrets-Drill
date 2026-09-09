#!/usr/bin/env python3
"""
Project 10 - The Secret Drill routine.

This routine requires SECRET_DRILL_TOKEN. It looks for the credential in
exactly two places, in order:

  1. The process environment  (os.environ)                 - provided by the
     execution environment / secrets panel.
  2. A local .env file in the working directory            - local fallback.

A fresh clone from Git will NOT contain .env because .env is gitignored and
never committed. A cloud run therefore succeeds only when the execution
environment supplies SECRET_DRILL_TOKEN.

Exit codes:
    0  SECRET FOUND   (task succeeded)
    1  SECRET MISSING (task failed)
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ENV_VAR_NAME = "SECRET_DRILL_TOKEN"
ENV_FILE = Path(".env")
MARKER = "secret-drill"


def load_env_file(path: Path) -> dict:
    """Minimal dependency-free .env parser."""
    values = {}
    if not path.exists():
        return values
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return values
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def redact(value: str) -> str:
    """Never reveal the credential value."""
    return "[REDACTED]" if value else "[EMPTY]"


def main() -> int:
    token = os.environ.get(ENV_VAR_NAME, "").strip()
    source = ""

    if token:
        source = "environment variable"
    else:
        env_values = load_env_file(ENV_FILE)
        if ENV_VAR_NAME in env_values and env_values[ENV_VAR_NAME].strip():
            token = env_values[ENV_VAR_NAME].strip()
            source = ".env file (local fallback)"

    run_id = os.environ.get("DRILL_RUN", "UNLABELED")
    now = datetime.now(timezone.utc).isoformat()
    env_var_configured = bool(os.environ.get(ENV_VAR_NAME, "").strip())

    result = {
        "run_id": run_id,
        "timestamp_utc": now,
        "env_var_SECRET_DRILL_TOKEN_configured": env_var_configured,
        "env_file_present": ENV_FILE.exists(),
        "credential_status": "FOUND" if token else "MISSING",
        "credential_source": source if token else "none",
        "credential_value": redact(token),
        "task_result": "SUCCESS" if token else "FAIL",
        "error": None,
    }

    if token:
        digest = hashlib.sha256(f"{MARKER}:{token}".encode("utf-8")).hexdigest()
        result["confirmation_artifact_sha256"] = digest
    else:
        result.pop("confirmation_artifact_sha256", None)
        result["error"] = (
            f"{ENV_VAR_NAME} was not available: no environment variable was set "
            "and no .env file exists in this environment."
        )

    log_dir = Path("drill_logs")
    log_dir.mkdir(exist_ok=True)
    safe_run_id = "".join(c if c.isalnum() else "_" for c in run_id)
    log_path = log_dir / f"drill_result_{safe_run_id.lower()}.json"
    log_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("=== Project 10 - The Secret Drill ===")
    print(f"Run ID: {run_id}")
    print(f"Environment variable {ENV_VAR_NAME}: "
          f"{'configured' if env_var_configured else 'not configured'}")
    print(f".env file present: {'yes' if ENV_FILE.exists() else 'no'}")
    print(f"Credential status: {result['credential_status']}")
    print(f"Credential source: {source if token else 'none'}")
    print(f"Credential value: {redact(token)}")
    print(f"Task result: {result['task_result']}")
    if token:
        print(f"Confirmation artifact (sha256): "
              f"{result['confirmation_artifact_sha256'][:16]}...")
    else:
        print(f"Error: {result['error']}")
    print(f"Evidence written to: {log_path}")

    return 0 if token else 1


if __name__ == "__main__":
    sys.exit(main())