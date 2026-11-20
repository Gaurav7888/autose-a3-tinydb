"""In-process tools. No shell. ADR-005."""

from __future__ import annotations

import os
import re
from pathlib import Path

READ_FILES = {"README.rst", "ARCHITECTURE.md", "pyproject.toml"}
READ_PREFIXES = ("tinydb/", "tests/")
WRITE_PREFIXES = ("tinydb/", "tests/")
BLOCKED_PREFIXES = (
    "experiment/",
    "results/",
    "workflow/",
    ".github/",
    "architecture/",
)


class ToolError(Exception):
    pass


def _relative(root: Path, raw: str) -> tuple[Path, str]:
    if not raw or not str(raw).strip():
        raise ToolError("path is empty")
    text = str(raw).strip().replace("\\", "/")
    if text.startswith("/") or re.match(r"^[A-Za-z]:", text):
        raise ToolError("absolute paths are refused")
    if "\x00" in text:
        raise ToolError("path is refused")
    root_resolved = root.resolve()
    candidate = (root_resolved / text).resolve()
    try:
        rel = candidate.relative_to(root_resolved).as_posix()
    except ValueError:
        raise ToolError("path escapes the repository") from None
    if rel.startswith(BLOCKED_PREFIXES) or rel in {"experiment", "results", "workflow", ".github", "architecture"}:
        raise ToolError(f"{rel} is outside the files this role may touch")
    return candidate, rel


def _readable(rel: str) -> None:
    if rel in READ_FILES or rel.startswith(READ_PREFIXES):
        return
    raise ToolError(f"{rel} is not readable by this role")


def _writable(rel: str) -> None:
    if rel.startswith(WRITE_PREFIXES) and not rel.endswith("/"):
        return
    raise ToolError(f"{rel} is not writable")


def read_file(root: Path, path: str, offset: int = 1, limit: int = 200) -> str:
    candidate, rel = _relative(root, path)
    _readable(rel)
    if not candidate.is_file():
        raise ToolError(f"{rel} is not a file")
    lines = candidate.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(1, int(offset))
    count = max(1, min(int(limit), 250))
    chunk = lines[start - 1:start - 1 + count]
    body = "\n".join(f"{number}|{line}" for number, line in enumerate(chunk, start))
    return body or "(empty)"


def search(root: Path, pattern: str, path: str = "tinydb") -> str:
    if not pattern or len(pattern) > 200:
        raise ToolError("pattern must be 1 to 200 characters")
    try:
        regex = re.compile(pattern)
    except re.error as exc:
        raise ToolError(f"bad pattern: {exc}") from exc
    base_path, rel = _relative(root, path)
    if base_path.is_file():
        _readable(rel)
        files = [base_path]
    elif rel in {"tinydb", "tests"} or rel.startswith(READ_PREFIXES):
        if not base_path.is_dir():
            raise ToolError(f"{rel} is not a directory")
        files = [item for item in base_path.rglob("*") if item.is_file()]
    else:
        raise ToolError(f"{rel} is not searchable")
    hits = []
    for item in files:
        item_rel = item.resolve().relative_to(root.resolve()).as_posix()
        if item_rel.startswith(BLOCKED_PREFIXES):
            continue
        if not (item_rel.startswith(READ_PREFIXES) or item_rel in READ_FILES):
            continue
        try:
            lines = item.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, 1):
            if regex.search(line):
                hits.append(f"{item_rel}:{number}:{line[:180]}")
                if len(hits) >= 30:
                    return "\n".join(hits)
    return "\n".join(hits) if hits else "no matches"


def replace(root: Path, path: str, old: str, new: str) -> str:
    if not old:
        raise ToolError("old is empty")
    candidate, rel = _relative(root, path)
    _writable(rel)
    if not candidate.is_file():
        raise ToolError(f"{rel} is not a file")
    text = candidate.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        raise ToolError("old string was not found")
    if count > 1:
        raise ToolError(f"old string matched {count} times; include more context")
    candidate.write_text(text.replace(old, new, 1), encoding="utf-8")
    return f"updated {rel}"


def write_file(root: Path, path: str, content: str) -> str:
    if content is None:
        raise ToolError("content is missing")
    if len(content) > 80_000:
        raise ToolError("content is too large")
    candidate, rel = _relative(root, path)
    _writable(rel)
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text(content, encoding="utf-8")
    return f"wrote {rel} ({len(content)} chars)"


def dispatch(root: Path, call: dict) -> str:
    name = str(call.get("tool") or "")
    try:
        if name == "read_file":
            return read_file(
                root,
                str(call.get("path") or ""),
                int(call.get("offset") or 1),
                int(call.get("limit") or 200),
            )
        if name == "search":
            return search(root, str(call.get("pattern") or ""), str(call.get("path") or "tinydb"))
        if name == "replace":
            return replace(
                root,
                str(call.get("path") or ""),
                str(call.get("old") or ""),
                str(call.get("new") if call.get("new") is not None else ""),
            )
        if name == "write_file":
            return write_file(root, str(call.get("path") or ""), str(call.get("content") or ""))
        raise ToolError(f"unknown tool {name}")
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001 - tool errors go back to the model, not the traceback
        raise ToolError(str(exc)) from exc


def clean_env(root: Path) -> dict[str, str]:
    """Environment for pytest: no tokens, and the repo on PYTHONPATH."""
    skip = {"ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY", "GH_TOKEN", "GITHUB_TOKEN"}
    env = {key: value for key, value in os.environ.items() if key not in skip}
    env["PYTHONPATH"] = str(root)
    return env
