# Sequence view

This is the sequence the workflow implements. The shape below was fixed before the agent code existed. One recorded run is linked at the bottom.

Happy path for a bug report. The vague issue is the same sequence and stops at the requirements check.

```mermaid
sequenceDiagram
  actor M as Maintainer
  participant G as gate
  participant A as Analyst Haiku
  participant C as Checks
  participant B as Builder Sonnet 4.6
  participant R as release and ci.yml
  participant V as Reviewer Sonnet 4.5
  actor H as Person

  M->>G: label autose on the issue
  G->>G: actor has write, no open autose PR
  G->>A: issue text inside untrusted tags, A1 skill
  A->>C: spec.md
  C->>C: verdict is not BLOCKED, every AC has setup, stimulus, outcome
  C->>A: spec.md, ARCHITECTURE.md, path and symbol tree
  A->>C: design.md
  C->>C: each path exists and each named symbol is in that file
  C->>B: spec.md and design.md
  B->>C: edits under tinydb/ and tests/
  C->>C: compileall, then pytest
  alt pytest fails and the retry budget remains
    C->>B: pytest output, no new privileges
    B->>C: further edits
    C->>C: pytest again
  end
  C->>R: branch autose/issue-N
  R->>R: open PR, workflow_dispatch ci.yml, wait for ci/pytest
  R->>V: issue text, diff, PR head, pytest log
  Note over V: no spec, no design, no builder transcript, contents read only
  V->>C: review.md
  alt request changes and this is round 1
    C->>B: review.md findings and the route code or approach
    B->>C: edits
    C->>R: push, CI again
    R->>V: fresh reviewer call on the new head
  end
  C->>H: approved, or two rounds used, or a check failed
  Note over H: the workflow does not merge
```

## Where a run stops

| Check that failed | What is saved | What happens next |
| --- | --- | --- |
| Requirements, including a `BLOCKED` verdict | `spec.md` with the reason | The run stops. No branch |
| Design | `design.md` with the checker errors | The run stops. No branch |
| Build, after the test retry and one design retry | `diff.patch`, `test_report.md` | The run stops. No pull request |
| CI | `pr.md` and the failing status | The run stops before review |
| Review round 2 still requests changes | `review.md` | The run stops. The PR stays open |

A model that asks to skip a check has no job it can start. The workflow file is the only place those edges exist.

## One recorded run

Issue 3, "Add an inclusive between test to Query", run [44876587072](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44876587072), pull request [#13](https://github.com/Gaurav7888/autose-a3-tinydb/pull/13).

The gate accepted the `autose` label. Requirements and design passed their checks. The builder edited `tinydb/queries.py` and the tests. Pytest passed, `ci.yml` passed, and the release job opened the pull request. The reviewer, in a separate job, read `queries.py` and requested a change: the hash tuple for `between` did not call `freeze` on the bounds. The rework job did not start. The pull request is still open. Hidden tests for that pull request later passed 3/3. The workflow did not merge.
