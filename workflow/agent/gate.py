"""Decide whether a trigger may start a run. ADR-010.

The issue body is not sent to a model from this file.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

MARKER = "<!-- autose-pr:"
RUNNING = "autose-running"


def first_line(body: str) -> str:
    text = (body or "").replace("\r\n", "\n").strip()
    if not text:
        return ""
    return text.split("\n", 1)[0].strip()


def decide(
    event_name: str,
    event: dict,
    actor: str,
    permission: str,
    marker_open: bool,
    running: bool,
    dispatch_issue: str = "",
    dispatch_variant: str = "split",
) -> dict:
    """Pure decision. `proceed` is 'true' or 'false' so Actions outputs stay strings."""
    refused = ""
    triggered = False
    issue_number = ""
    mode = "full"
    variant = "split"
    pr_number = ""
    branch = ""

    if actor.endswith("[bot]"):
        return _result(False, "", "full", "split", "", "", "bots cannot start a run")

    if event_name == "workflow_dispatch":
        triggered = True
        issue_number = str(dispatch_issue or "").strip()
        variant = dispatch_variant if dispatch_variant in {"split", "monolith"} else "split"
        mode = "full"
        if not issue_number.isdigit():
            refused = "workflow_dispatch needs an issue number"
    elif event_name == "issues":
        label = ((event.get("label") or {}).get("name")) or ""
        if label != "autose":
            return _result(False, "", "full", "split", "", "", "")
        triggered = True
        issue_number = str((event.get("issue") or {}).get("number") or "")
    elif event_name == "issue_comment":
        comment = (event.get("comment") or {}).get("body") or ""
        if first_line(comment) != "/autose":
            return _result(False, "", "full", "split", "", "", "")
        triggered = True
        issue = event.get("issue") or {}
        issue_number = str(issue.get("number") or "")
        if issue.get("pull_request"):
            mode = "review"
            pr_number = issue_number
    else:
        return _result(False, "", "full", "split", "", "", "")

    if not triggered:
        return _result(False, "", mode, variant, pr_number, branch, "")

    if permission not in {"admin", "write"}:
        refused = refused or "only a collaborator with write access can start AutoSE"
    if mode == "full" and marker_open:
        refused = refused or "this issue already has an open AutoSE pull request"
    if mode == "full" and running:
        refused = refused or "an AutoSE run is already marked in progress for this issue"
    if not issue_number:
        refused = refused or "no issue number"

    proceed = not refused
    return _result(proceed, issue_number, mode, variant, pr_number, branch, refused)


def _result(proceed, issue_number, mode, variant, pr_number, branch, reason) -> dict:
    return {
        "proceed": "true" if proceed else "false",
        "issue_number": issue_number,
        "mode": mode,
        "variant": variant,
        "pr_number": pr_number,
        "branch": branch,
        "reason": reason,
    }


def _api(path: str) -> dict | list:
    raw = subprocess.check_output(["gh", "api", path], text=True)
    return json.loads(raw)


def _comment(repo: str, issue_number: str, body: str) -> None:
    if not issue_number:
        return
    subprocess.run(
        ["gh", "issue", "comment", issue_number, "--repo", repo, "--body", body],
        check=False,
    )


def _write_outputs(values: dict) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    lines = [f"{key}={value}" for key, value in values.items()]
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    else:
        print("\n".join(lines))


def _permission(repo: str, actor: str) -> str:
    try:
        payload = _api(f"repos/{repo}/collaborators/{actor}/permission")
    except subprocess.CalledProcessError:
        return ""
    if isinstance(payload, dict):
        return str(payload.get("permission") or "")
    return ""


def _marker_open(repo: str, issue_number: str) -> bool:
    try:
        comments = _api(f"repos/{repo}/issues/{issue_number}/comments?per_page=100")
    except subprocess.CalledProcessError:
        return False
    if not isinstance(comments, list):
        return False
    number = ""
    for comment in comments:
        body = comment.get("body") or ""
        if MARKER in body:
            # <!-- autose-pr: 12 branch: autose/issue-3 -->
            try:
                number = body.split(MARKER, 1)[1].split(" ", 1)[0].strip()
            except IndexError:
                number = ""
    if not number.isdigit():
        return False
    try:
        pr = _api(f"repos/{repo}/pulls/{number}")
    except subprocess.CalledProcessError:
        return False
    return isinstance(pr, dict) and pr.get("state") == "open"


def _running(event: dict, repo: str, issue_number: str) -> bool:
    labels = ((event.get("issue") or {}).get("labels")) or []
    if any((label.get("name") == RUNNING) for label in labels if isinstance(label, dict)):
        return True
    try:
        live = _api(f"repos/{repo}/issues/{issue_number}/labels")
    except subprocess.CalledProcessError:
        return False
    return isinstance(live, list) and any(item.get("name") == RUNNING for item in live)


def _add_running(repo: str, issue_number: str) -> None:
    subprocess.run(
        ["gh", "label", "create", RUNNING, "--repo", repo, "--color", "5319e7", "--force"],
        check=False,
    )
    subprocess.run(
        ["gh", "issue", "edit", issue_number, "--repo", repo, "--add-label", RUNNING],
        check=False,
    )


def main() -> int:
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    event = {}
    if event_path and os.path.exists(event_path):
        with open(event_path, encoding="utf-8") as handle:
            event = json.load(handle)
    actor = os.environ.get("GITHUB_ACTOR", "")
    repo = os.environ.get("GH_REPO") or os.environ.get("GITHUB_REPOSITORY", "")
    permission = _permission(repo, actor) if repo and actor else ""
    issue_guess = str((event.get("issue") or {}).get("number") or os.environ.get("ISSUE_NUMBER") or "")
    marker = False
    running = False
    label = ((event.get("label") or {}).get("name")) or ""
    comment = first_line(((event.get("comment") or {}).get("body")) or "")
    attempted = event_name == "workflow_dispatch" or label == "autose" or comment == "/autose"
    if attempted and issue_guess.isdigit() and repo and "pull_request" not in (event.get("issue") or {}):
        marker = _marker_open(repo, issue_guess)
        running = _running(event, repo, issue_guess)
    result = decide(
        event_name,
        event,
        actor,
        permission,
        marker,
        running,
        os.environ.get("ISSUE_NUMBER", ""),
        os.environ.get("VARIANT") or "split",
    )
    if result["proceed"] == "true" and result["mode"] == "review" and repo:
        try:
            pr = _api(f"repos/{repo}/pulls/{result['pr_number']}")
            result["branch"] = ((pr.get("head") or {}).get("ref")) or ""
        except subprocess.CalledProcessError:
            result["proceed"] = "false"
            result["reason"] = "could not read the pull request head"
    if result["reason"] and result["issue_number"]:
        _comment(repo, result["issue_number"], f"AutoSE did not start. {result['reason']}.")
    elif result["proceed"] == "true" and result["mode"] == "full":
        _add_running(repo, result["issue_number"])
        _comment(
            repo,
            result["issue_number"],
            f"AutoSE started ({result['variant']}). A person still decides whether to merge.",
        )
    _write_outputs({key: result[key] for key in ("proceed", "issue_number", "mode", "variant", "pr_number", "branch")})
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
