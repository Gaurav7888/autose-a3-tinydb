import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import checks


GOOD_SPEC = """
# Requirements specification
Document verdict: READY_FOR_IMPLEMENTATION

## Acceptance criteria

### AC-1
Setup: a table with one document {"name": "a"} and one document {"name": "b", "n": 3}
Stimulus: update every document with increment("n")
Outcome: the first document has n equal to 1 and the second has n equal to 4
"""

BLOCKED = """
# Requirements specification
Document verdict: BLOCKED

## Acceptance criteria
"""

PATHY = """
Document verdict: PARTIAL

## Acceptance criteria

### AC-1
Setup: an empty database
Stimulus: call between
Outcome: edit tinydb/queries.py so 5 matches
"""


def test_spec_accepts_concrete_outcome():
    ok, reason = checks.check_spec(GOOD_SPEC)
    assert ok, reason


def test_spec_stops_on_blocked():
    ok, reason = checks.check_spec(BLOCKED)
    assert not ok
    assert reason.startswith("BLOCKED")


def test_spec_rejects_paths_and_vague_words():
    ok, reason = checks.check_spec(PATHY)
    assert not ok
    assert "paths" in reason
    vague = """
Document verdict: PARTIAL
## Acceptance criteria
### AC-1
Setup: a database
Stimulus: open it
Outcome: faster and smarter
"""
    ok, reason = checks.check_spec(vague)
    assert not ok
    assert "quality" in reason


def test_design_accepts_existing_and_new_symbols(tmp_path):
    source = tmp_path / "tinydb"
    source.mkdir()
    (source / "queries.py").write_text("class Query:\n    def one_of(self):\n        return 1\n", encoding="utf-8")
    text = """
## Files
- `tinydb/queries.py` :: `one_of`
- `tinydb/queries.py` :: `between` new
"""
    ok, reason = checks.check_design(text, tmp_path)
    assert ok, reason


def test_design_rejects_invented_file(tmp_path):
    ok, reason = checks.check_design("- `tinydb/missing.py` :: `nope`\n", tmp_path)
    assert not ok
    assert "does not exist" in reason
