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
    1. GIT_SHA environment variable (set via Docker ARG/ENV at build time).
    2. git rev-parse at runtime (local dev only; skipped if git unavailable).
    3. "unknown" as safe fallback.
    """
    sha = os.environ.get("GIT_SHA", "").strip()
    if sha:
        return sha[:8]

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
