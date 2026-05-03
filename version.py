"""
App version resolution.

Reads GIT_SHA from the environment variable baked in at Docker build time.
Falls back to querying git at runtime (useful for local development).
"""

import os
import subprocess


def get_git_sha() -> str:
    """Return the git SHA for the running build.

    Resolution order:
    1. GIT_SHA environment variable (set via Docker ARG/ENV or deploy env).
    2. APP_VERSION environment variable (optional explicit override).
    3. K_REVISION environment variable (Cloud Run revision fallback).
    4. git rev-parse at runtime (local dev only; skipped if git unavailable).
    5. "unknown" as safe fallback.
    """
    for env_name in ("GIT_SHA", "APP_VERSION", "K_REVISION"):
        value = os.environ.get(env_name, "").strip()
        if value:
            return value[:32]

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return "unknown"


APP_VERSION = get_git_sha()
