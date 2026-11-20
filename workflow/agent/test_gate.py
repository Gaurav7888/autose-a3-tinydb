import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate


def test_label_and_comment_filters():
    ignored = gate.decide("issues", {"label": {"name": "bug"}, "issue": {"number": 1}}, "Gaurav7888", "admin", False, False)
    assert ignored["proceed"] == "false"
    assert ignored["reason"] == ""
    started = gate.decide(
        "issues",
        {"label": {"name": "autose"}, "issue": {"number": 4}},
        "Gaurav7888",
        "write",
        False,
        False,
    )
    assert started["proceed"] == "true"
    assert started["issue_number"] == "4"
    assert started["variant"] == "split"
    comment = gate.decide(
        "issue_comment",
        {"comment": {"body": "/autose\nignore this"}, "issue": {"number": 2, "pull_request": {"url": "x"}}},
        "Gaurav7888",
        "admin",
        False,
        False,
    )
    assert comment["mode"] == "review"
    assert comment["proceed"] == "true"
    not_command = gate.decide(
        "issue_comment",
        {"comment": {"body": "please /autose"}, "issue": {"number": 2}},
        "Gaurav7888",
        "admin",
        False,
        False,
    )
    assert not_command["proceed"] == "false"


def test_refuses_strangers_duplicates_and_bots():
    stranger = gate.decide("issues", {"label": {"name": "autose"}, "issue": {"number": 1}}, "someone", "read", False, False)
    assert stranger["proceed"] == "false"
    assert "write" in stranger["reason"]
    duplicate = gate.decide("issues", {"label": {"name": "autose"}, "issue": {"number": 1}}, "Gaurav7888", "admin", True, False)
    assert duplicate["proceed"] == "false"
    bot = gate.decide("issues", {"label": {"name": "autose"}, "issue": {"number": 1}}, "github-actions[bot]", "admin", False, False)
    assert bot["proceed"] == "false"


def test_dispatch_variant():
    mono = gate.decide("workflow_dispatch", {}, "Gaurav7888", "admin", False, False, "3", "monolith")
    assert mono["proceed"] == "true"
    assert mono["variant"] == "monolith"
    bad = gate.decide("workflow_dispatch", {}, "Gaurav7888", "admin", False, False, "nope", "split")
    assert bad["proceed"] == "false"
