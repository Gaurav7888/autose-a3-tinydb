import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run
import tools


def test_extracts_tool_json_with_braces_inside_strings():
    text = 'note\n{"tool":"write_file","path":"tests/t.py","content":"def f():\\n    return {1: 2}\\n"}\n'
    call = run.extract_call(text)
    assert call["tool"] == "write_file"
    assert "{1: 2}" in call["content"]


def test_refuses_escape_and_hidden_tests(tmp_path):
    (tmp_path / "tinydb").mkdir()
    (tmp_path / "experiment" / "hidden_tests").mkdir(parents=True)
    (tmp_path / "experiment" / "hidden_tests" / "test_secret.py").write_text("SECRET = 1\n", encoding="utf-8")
    (tmp_path / "tinydb" / "operations.py").write_text("def increment(field):\n    return field\n", encoding="utf-8")
    try:
        tools.read_file(tmp_path, "../tinydb/operations.py")
        raised = False
    except tools.ToolError:
        raised = True
    assert raised
    try:
        tools.read_file(tmp_path, "experiment/hidden_tests/test_secret.py")
        raised = False
    except tools.ToolError:
        raised = True
    assert raised
    message = tools.replace(
        tmp_path,
        "tinydb/operations.py",
        "return field",
        "return field + 1",
    )
    assert "updated" in message
    try:
        tools.write_file(tmp_path, "workflow/agent/x.py", "print(1)\n")
        raised = False
    except tools.ToolError:
        raised = True
    assert raised


def test_override_blocks_unread_approval():
    verdict, route, reason = run._override("APPROVE", "none", [], {"tinydb/queries.py"}, True)
    assert verdict == "REQUEST_CHANGES"
    assert "reading" in reason
    verdict, route, reason = run._override("APPROVE", "none", ["tinydb/queries.py"], {"tinydb/queries.py"}, False)
    assert verdict == "REQUEST_CHANGES"
    assert reason == "pytest failed"
    verdict, route, reason = run._override("APPROVE", "none", ["tinydb/queries.py"], {"tinydb/queries.py"}, True)
    assert verdict == "APPROVE"
    assert route == "none"
