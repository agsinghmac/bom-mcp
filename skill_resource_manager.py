"""Skill resource discovery, caching, and refresh management."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import logging
import re
import time
from typing import Dict

LOG = logging.getLogger(__name__)


@dataclass
class RefreshDiagnostic:
    """Structured diagnostic emitted during refresh."""

    severity: str
    code: str
    message: str
    file_path: str | None = None
    action_hint: str | None = None


@dataclass
class RefreshResult:
    """Summary for one refresh cycle."""

    mode: str
    started_at: float
    completed_at: float
    files_seen: int
    files_changed: int
    files_failed: int
    status: str
    diagnostics: list[RefreshDiagnostic] = field(default_factory=list)


@dataclass
class SkillEntry:
    """Parsed and cached skill resource content."""

    uri: str
    name: str
    description: str
    content: str
    source_path: str
    mtime_ns: int
    size_bytes: int
    parse_status: str = "VALID"
    errors: list[str] = field(default_factory=list)
    refreshed_at: float = field(default_factory=time.time)


class SkillResourceManager:
    """Discovers markdown skills, caches parsed output, and builds index content."""

    def __init__(self, skill_dir: Path, poll_interval_seconds: float = 30.0):
        self.skill_dir = skill_dir
        self.poll_interval_seconds = poll_interval_seconds
        self._entries_by_uri: Dict[str, SkillEntry] = {}
        self._cache_by_path: Dict[str, SkillEntry] = {}
        self._last_known_good_by_path: Dict[str, SkillEntry] = {}
        self._last_refresh_monotonic = 0.0
        self._last_result = RefreshResult(
            mode="STARTUP",
            started_at=time.time(),
            completed_at=time.time(),
            files_seen=0,
            files_changed=0,
            files_failed=0,
            status="OK",
            diagnostics=[],
        )

    @staticmethod
    def _normalize_skill_name(raw_name: str) -> str:
        normalized = raw_name.strip().lower().replace(" ", "-")
        normalized = re.sub(r"[^a-z0-9_-]+", "-", normalized)
        normalized = re.sub(r"-+", "-", normalized).strip("-")
        return normalized or "skill"

    @staticmethod
    def _extract_frontmatter(markdown_text: str) -> dict[str, str]:
        if not markdown_text.startswith("---\n"):
            return {}
        marker = "\n---\n"
        end_idx = markdown_text.find(marker, 4)
        if end_idx == -1:
            return {}
        data: dict[str, str] = {}
        for line in markdown_text[4:end_idx].splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            data[key.strip().lower()] = value.strip().strip('"').strip("'")
        return data

    @staticmethod
    def _extract_heading(markdown_text: str) -> str | None:
        for line in markdown_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("# ") and len(stripped) > 2:
                return stripped[2:].strip()
        return None

    @staticmethod
    def _extract_first_paragraph(markdown_text: str) -> str | None:
        lines = markdown_text.splitlines()
        idx = 0
        while idx < len(lines) and (not lines[idx].strip() or lines[idx].strip().startswith("#")):
            idx += 1
        paragraph_lines: list[str] = []
        while idx < len(lines):
            line = lines[idx].strip()
            if not line:
                break
            if line.startswith("#"):
                break
            paragraph_lines.append(line)
            idx += 1
        if not paragraph_lines:
            return None
        return " ".join(paragraph_lines)

    def _build_entry_from_file(self, path: Path, mtime_ns: int, size_bytes: int) -> SkillEntry:
        text = path.read_text(encoding="utf-8")
        normalized_name = self._normalize_skill_name(path.stem)
        uri = f"skill://{normalized_name}"

        frontmatter = self._extract_frontmatter(text)
        heading = self._extract_heading(text)
        description = (
            frontmatter.get("summary")
            or frontmatter.get("description")
            or self._extract_first_paragraph(text)
            or f"Skill instructions from {path.name}."
        )

        errors: list[str] = []
        parse_status = "VALID"
        if not heading:
            parse_status = "DEGRADED"
            errors.append("Missing markdown H1 heading; filename fallback used for name.")

        if description == f"Skill instructions from {path.name}.":
            parse_status = "DEGRADED"
            errors.append("Missing descriptive paragraph; generated fallback description.")

        display_name = heading or path.stem.replace("_", " ").replace("-", " ").title()

        return SkillEntry(
            uri=uri,
            name=display_name,
            description=description,
            content=text,
            source_path=str(path),
            mtime_ns=mtime_ns,
            size_bytes=size_bytes,
            parse_status=parse_status,
            errors=errors,
        )

    def refresh(self, mode: str = "MANUAL") -> RefreshResult:
        started_at = time.time()
        files_seen = 0
        files_changed = 0
        files_failed = 0
        diagnostics: list[RefreshDiagnostic] = []

        if not self.skill_dir.exists():
            diagnostics.append(
                RefreshDiagnostic(
                    severity="WARN",
                    code="SKILL_DIR_MISSING",
                    message=f"Skill directory not found: {self.skill_dir}",
                    action_hint="Create the .skills directory and add markdown files.",
                )
            )
            self._entries_by_uri = {}
            self._cache_by_path = {}
            status = "PARTIAL"
            result = RefreshResult(
                mode=mode,
                started_at=started_at,
                completed_at=time.time(),
                files_seen=0,
                files_changed=0,
                files_failed=1,
                status=status,
                diagnostics=diagnostics,
            )
            self._last_result = result
            self._last_refresh_monotonic = time.monotonic()
            for diag in diagnostics:
                LOG.warning("%s: %s", diag.code, diag.message)
            return result

        discovered_files = sorted(self.skill_dir.glob("*.md"))
        next_entries: Dict[str, SkillEntry] = {}
        next_cache: Dict[str, SkillEntry] = {}

        for path in discovered_files:
            files_seen += 1
            path_key = str(path)
            try:
                stat = path.stat()
            except OSError as exc:
                files_failed += 1
                diagnostics.append(
                    RefreshDiagnostic(
                        severity="ERROR",
                        code="SKILL_STAT_FAILED",
                        message=f"Failed to stat skill file: {exc}",
                        file_path=path_key,
                    )
                )
                continue

            cached = self._cache_by_path.get(path_key)
            if cached and cached.mtime_ns == stat.st_mtime_ns and cached.size_bytes == stat.st_size:
                entry = cached
            else:
                files_changed += 1
                try:
                    entry = self._build_entry_from_file(path, stat.st_mtime_ns, stat.st_size)
                except Exception as exc:  # pylint: disable=broad-except
                    files_failed += 1
                    error_msg = f"Failed to parse skill file: {exc}"
                    diagnostics.append(
                        RefreshDiagnostic(
                            severity="ERROR",
                            code="SKILL_PARSE_FAILED",
                            message=error_msg,
                            file_path=path_key,
                            action_hint="Fix markdown formatting or encoding for this skill file.",
                        )
                    )
                    lkg = self._last_known_good_by_path.get(path_key)
                    if not lkg:
                        continue
                    entry = SkillEntry(
                        uri=lkg.uri,
                        name=lkg.name,
                        description=lkg.description,
                        content=lkg.content,
                        source_path=lkg.source_path,
                        mtime_ns=lkg.mtime_ns,
                        size_bytes=lkg.size_bytes,
                        parse_status="DEGRADED",
                        errors=[error_msg],
                    )
                else:
                    self._last_known_good_by_path[path_key] = entry

            if entry.uri in next_entries:
                files_failed += 1
                diagnostics.append(
                    RefreshDiagnostic(
                        severity="ERROR",
                        code="SKILL_URI_COLLISION",
                        message=f"Multiple files resolved to URI {entry.uri}",
                        file_path=path_key,
                        action_hint="Rename files to unique names after normalization.",
                    )
                )
                continue

            next_entries[entry.uri] = entry
            next_cache[path_key] = entry

        removed_paths = set(self._cache_by_path) - set(next_cache)
        for removed_path in removed_paths:
            self._last_known_good_by_path.pop(removed_path, None)

        if files_failed and next_entries:
            status = "PARTIAL"
        elif files_failed and not next_entries:
            status = "FAILED"
        else:
            status = "OK"

        result = RefreshResult(
            mode=mode,
            started_at=started_at,
            completed_at=time.time(),
            files_seen=files_seen,
            files_changed=files_changed,
            files_failed=files_failed,
            status=status,
            diagnostics=diagnostics,
        )

        self._entries_by_uri = next_entries
        self._cache_by_path = next_cache
        self._last_result = result
        self._last_refresh_monotonic = time.monotonic()

        for diag in diagnostics:
            log_fn = LOG.error if diag.severity == "ERROR" else LOG.warning
            log_fn("%s: %s", diag.code, diag.message)

        return result

    def refresh_if_due(self) -> RefreshResult | None:
        if (time.monotonic() - self._last_refresh_monotonic) < self.poll_interval_seconds:
            return None
        return self.refresh(mode="PERIODIC")

    def list_skills(self, refresh_if_due: bool = True) -> list[SkillEntry]:
        if refresh_if_due:
            self.refresh_if_due()
        return [self._entries_by_uri[uri] for uri in sorted(self._entries_by_uri)]

    def get_skill_by_name(self, skill_name: str) -> SkillEntry:
        normalized_name = self._normalize_skill_name(skill_name)
        uri = f"skill://{normalized_name}"
        entry = self._entries_by_uri.get(uri)
        if not entry:
            raise KeyError(uri)
        return entry

    def get_skill_content(self, skill_name: str) -> str:
        return self.get_skill_by_name(skill_name).content

    def get_index_content(self) -> str:
        entries = self.list_skills(refresh_if_due=False)
        result = self._last_result

        lines = [
            "# Skill Index",
            "",
            f"- Last refresh: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(result.completed_at))}",
            f"- Refresh mode: {result.mode}",
            f"- Refresh status: {result.status}",
            f"- Files seen: {result.files_seen}",
            f"- Files changed: {result.files_changed}",
            f"- Files failed: {result.files_failed}",
            "",
            "## Skills",
            "",
        ]

        if not entries:
            lines.append("No discoverable markdown skills were found in `.skills/`.")
        else:
            for entry in entries:
                status = entry.parse_status
                lines.append(f"- {entry.uri}")
                lines.append(f"  - Name: {entry.name}")
                lines.append(f"  - Description: {entry.description}")
                lines.append(f"  - Status: {status}")

        if result.diagnostics:
            lines.extend(["", "## Diagnostics", ""])
            for diag in result.diagnostics:
                location = f" ({diag.file_path})" if diag.file_path else ""
                lines.append(f"- [{diag.severity}] {diag.code}: {diag.message}{location}")

        return "\n".join(lines) + "\n"
