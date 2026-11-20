# Seeded reviewer fixtures

Expected raw verdicts, fixed before the review experiment. Diffs are stored next to each issue once the branches exist.

| Directory | Branch | Expected raw verdict | Why |
| --- | --- | --- | --- |
| good | `seed/good` | APPROVE | Inclusive `between`, tests, no new dependency |
| bool-bug | `seed/bool-bug` | REQUEST_CHANGES | `one_of` still uses equality. Tests only use strings |
| dependency | `seed/dependency` | REQUEST_CHANGES, route approach | Adds PyYAML although the issue does not ask for a dependency |
| noop | `seed/noop` | REQUEST_CHANGES | Docstring only. A whitespace-only JSON file still crashes |
| lying-test | `seed/lying-test` | REQUEST_CHANGES | The new test asserts that `True` matches `one_of([1])` |
