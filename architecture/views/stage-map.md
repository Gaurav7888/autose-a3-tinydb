# Stage map

The stages and the checks are the ones in the assignment. The agent column is the decision recorded in ADR-001. The pass or fail column is ADR-007: a Python check, not the model.

| Stage | Agent | Reads | Writes | Artifact | Check before the next stage | Who decides |
| --- | --- | --- | --- | --- | --- | --- |
| 1 Requirements | Analyst, requirements prompt, `claude-haiku-4-5` | Issue title and body, A1 skill | `spec.md` only | `spec.md` | Verdict is not `BLOCKED`. At least one `AC-n`. Each AC has `Setup`, `Stimulus` and `Outcome`. The AC section names no repository path | `workflow/agent/checks.py` |
| 2 Design | Analyst, design prompt, `claude-haiku-4-5` | `spec.md`, `ARCHITECTURE.md`, path-and-symbol tree | `design.md` only | `design.md` | At least one `` `path` :: `symbol` `` bullet. The path exists. The symbol is already defined in that file, or the bullet is marked `new` | `workflow/agent/checks.py` |
| 3 Implementation | Builder, `claude-sonnet-4-6` | `spec.md`, `design.md`, `tinydb/`, `tests/` | Files under `tinydb/` and `tests/` | `diff.patch` | `compileall` on `tinydb` and `tests`, then `import tinydb` | harness |
| 4 Testing | Builder for edits, harness for the run | The tree and, on a retry, pytest output | Further edits in the same trees, then `test_report.md` | `test_report.md` | `pytest -q -o addopts=` exits 0, and the diff changes a file under `tinydb/`. Two failures retry implementation. A third failure may request one design retry. After that the run stops | pytest's exit code |
| 5 Release | none | The branch | Push, PR, commit status | `pr.md` and the PR URL | PR state is open and `ci/pytest` on the head SHA is success | `gh` and the commit status |
| 6 Review | Reviewer, `claude-sonnet-4-5` | Issue, diff, PR head, harness pytest log | `review.md` | `review.md` | A posted verdict. `APPROVE` is rewritten to `REQUEST_CHANGES` if pytest failed or the reviewer read no file from the diff. At most two rounds. A code route returns to stage 3. An approach route returns to stage 2 and then 3 | harness for the mechanical rules, then the person for merge |

Hidden acceptance tests are not a stage. They are not in the agent's tree. They are run afterwards, from `experiment/hidden_tests/`, against the PR head, and the result goes in `results/results.csv`.
