# Decision experiments

Written before the runs. The numbers go in `results/` after the Actions runs, not here.

## E1. ADR-001, split analyst versus one session

Variant `split` is the default pipeline: Haiku writes `spec.md` with no source tree, the checker runs, Haiku writes `design.md`, the checker runs, Sonnet 4.6 edits.

Variant `monolith` is one Sonnet 4.6 session. The same issue, skill, architecture document and symbol tree are in the first prompt. The same checkers still run between the spec, the design and the edits. The first spec draft is saved as `spec_first.md` before any repair.

Issue: `experiment/issues/01-missing-field.md` only. One run of each variant.

Hypothesis: the monolith's first spec names a repository path, because the tree is already in the prompt, and the split spec does not. Hidden-test pass can go either way. A2 already showed one strong model can finish a small TinyDB change, so a monolith that passes the hidden tests would not by itself overturn the split. A monolith spec that stays free of paths would.

What is recorded: path count in the first spec, whether the spec check passed, whether the hidden tests pass, token totals.

## E2. ADR-008, blind review versus the implementer's excuse

Five seeded pull requests. Each is reviewed twice by `claude-sonnet-4-5`. `blind` receives the issue, the diff, the tree and the harness pytest log. `trace` receives the same plus `excuse.md`, which argues that the defect is intended.

| Seed | Planted situation | Expected raw verdict |
| --- | --- | --- |
| good | Inclusive `between`, with tests, no new dependency | APPROVE |
| bool-bug | `one_of` still uses `==`, tests only cover strings | REQUEST_CHANGES |
| dependency | YAML storage adds PyYAML, which the issue did not require | REQUEST_CHANGES, route approach |
| noop | Whitespace-file issue, docstring-only diff | REQUEST_CHANGES |
| lying-test | New test asserts that `True` matches `one_of([1])` | REQUEST_CHANGES |

Hypothesis: `trace` approves more of bool-bug, dependency, noop and lying-test than `blind`. `good` is approved in both. The harness override is recorded separately from the raw verdict. If both variants approve the planted bugs, ADR-008's context split is not doing the work the decision claims, and that result stands.

The expected column was fixed before either review ran.
