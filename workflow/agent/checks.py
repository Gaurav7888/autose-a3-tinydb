"""Stage checks. The model does not grade itself. ADR-007."""

from __future__ import annotations

import re
from pathlib import Path

QUARANTINE = {
    "autonomous",
    "intelligent",
    "smart",
    "smarter",
    "robust",
    "scalable",
    "enterprise",
    "enterprise-grade",
    "seamless",
    "intuitive",
    "easy",
    "easier",
    "fast",
    "faster",
    "secure",
    "private",
    "reliable",
    "modern",
    "user-friendly",
    "flexible",
    "powerful",
    "real-time",
    "high-quality",
    "comprehensive",
    "end-to-end",
    "world-class",
}

_STOPWORDS = {
    "a",
    "an",
    "the",
    "to",
    "of",
    "and",
    "or",
    "be",
    "is",
    "are",
    "it",
    "its",
    "this",
    "that",
    "for",
    "with",
    "on",
    "in",
    "as",
    "by",
    "at",
}

_VERDICT = re.compile(
    r"\*{0,2}\s*Document verdict:\*{0,2}\s*(BLOCKED|PARTIAL|READY_FOR_IMPLEMENTATION)\b",
    re.I,
)
_AC = re.compile(r"^###\s+AC-(\d+)\s*$", re.M)
_FIELD = re.compile(r"^(Setup|Stimulus|Outcome):\s*(.+)$", re.M)
_BULLET = re.compile(
    r"`([^`\n]+)`\s*::\s*`([^`\n]+)`(?:\s+\**new\**)?",
    re.I,
)
_NEW = re.compile(
    r"`([^`\n]+)`\s*::\s*`([^`\n]+)`\s+\**new\**",
    re.I,
)
_SYMBOL = re.compile(r"^(?:async\s+def|def|class)\s+([A-Za-z_][A-Za-z0-9_]*)\b", re.M)
_PATH = re.compile(
    r"\b(?:tinydb|tests|experiment|workflow|architecture|docs)/[\w./-]+|\b[\w.-]+\.(?:py|rst|md|toml|yml)\b"
)


def _section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.M | re.I)
    match = pattern.search(text)
    if not match:
        return ""
    rest = text[match.end():]
    nxt = re.search(r"^##\s+", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


def acceptance_paths(text: str) -> list[str]:
    """Paths named inside the acceptance criteria. The monolith comparison counts these."""
    return sorted(set(_PATH.findall(_section(text, "Acceptance criteria"))))


def check_spec(text: str) -> tuple[bool, str]:
    """Return (passed, reason). BLOCKED is a failed check and stops the run."""
    if not text or not text.strip():
        return False, "spec.md is empty"
    verdict = _VERDICT.search(text)
    if not verdict:
        return False, "missing a line 'Document verdict: BLOCKED|PARTIAL|READY_FOR_IMPLEMENTATION'"
    if verdict.group(1) == "BLOCKED":
        return False, "BLOCKED: the issue does not state a testable behaviour, so the run stops"
    ac_text = _section(text, "Acceptance criteria")
    if not ac_text:
        return False, "missing an '## Acceptance criteria' section"
    leaked = sorted(set(_PATH.findall(ac_text)))
    if leaked:
        return False, "acceptance criteria name repository paths: " + ", ".join(leaked[:8])
    headers = list(_AC.finditer(ac_text))
    if not headers:
        return False, "no '### AC-n' blocks under Acceptance criteria"
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(ac_text)
        block = ac_text[header.end():end]
        fields = {name: value.strip() for name, value in _FIELD.findall(block)}
        missing = [name for name in ("Setup", "Stimulus", "Outcome") if not fields.get(name)]
        if missing:
            return False, f"AC-{header.group(1)} is missing {', '.join(missing)}"
        outcome = fields["Outcome"]
        if re.search(r"backdoor", outcome, re.I):
            return False, f"AC-{header.group(1)} asks for a backdoor"
        words = [
            word.lower()
            for word in re.findall(r"[A-Za-z][A-Za-z-]+", outcome)
            if word.lower() not in _STOPWORDS
        ]
        if words and all(word in QUARANTINE for word in words):
            return False, f"AC-{header.group(1)} outcome is only an unmeasured quality word"
    return True, f"{len(headers)} testable acceptance criteria"


def _symbols(path: Path) -> set[str]:
    try:
        return set(_SYMBOL.findall(path.read_text(encoding="utf-8")))
    except OSError:
        return set()


def check_design(text: str, root: Path) -> tuple[bool, str]:
    if not text or not text.strip():
        return False, "design.md is empty"
    bullets = list(_BULLET.finditer(text))
    if not bullets:
        return False, "no `path` :: `symbol` bullets"
    new_ones = {(m.group(1).strip(), m.group(2).strip()) for m in _NEW.finditer(text)}
    problems = []
    accepted = 0
    for match in bullets:
        rel = match.group(1).strip().lstrip("./")
        symbol = match.group(2).strip().split(".")[-1]
        path = (root / rel).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            problems.append(f"{rel} escapes the repository")
            continue
        if not path.is_file():
            problems.append(f"{rel} does not exist")
            continue
        is_new = (match.group(1).strip(), match.group(2).strip()) in new_ones
        if is_new:
            accepted += 1
            continue
        if symbol not in _symbols(path):
            problems.append(f"{symbol} is not defined in {rel} (mark it `new` if you are adding it)")
            continue
        accepted += 1
    if accepted == 0:
        detail = "; ".join(problems[:8]) or "no usable bullet"
        return False, detail
    if problems:
        return True, f"{accepted} file entries; ignored: " + "; ".join(problems[:4])
    return True, f"{accepted} file entries"
