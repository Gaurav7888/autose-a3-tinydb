# Runs

Repository: https://github.com/Gaurav7888/autose-a3-tinydb

Stage tokens below are input plus output from the uploaded `usage.json` files. Review calls are not in those files. The recorded total for the rows in `results.csv` is 452,567.

## Issues

| Issue | What happened | Run | Pull request | Review |
| --- | --- | --- | --- | --- |
| 1 missing field | Spec, design, build, release. Hidden tests 4/4. Review posted later, APPROVE. | [44812405332](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44812405332) | [#6](https://github.com/Gaurav7888/autose-a3-tinydb/pull/6) | [44876554203](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44876554203) |
| 2 one_of types | Same shape. Hidden tests 3/3. Review APPROVE. | [44813347926](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44813347926) | [#12](https://github.com/Gaurav7888/autose-a3-tinydb/pull/12) | [44876555214](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44876555214) |
| 3 between | Full pipeline. Hidden tests 3/3. Review REQUEST_CHANGES. Rework did not start. | [44876587072](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44876587072) | [#13](https://github.com/Gaurav7888/autose-a3-tinydb/pull/13) | same run |
| 4 cache size | Full pipeline. Hidden tests 4/4. Review APPROVE. | [44876594199](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44876594199) | [#14](https://github.com/Gaurav7888/autose-a3-tinydb/pull/14) | same run |
| 5 vague | Requirements verdict BLOCKED. No branch, no pull request. | [44812524807](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44812524807) | none | none |

CI on the pull requests is `ci.yml` (`pytest` on Python 3.12). It passed on the opened pull requests. The upstream matrix is skipped on this fork.

## Experiments

Monolith on issue 1: [44877586615](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44877586615). The spec named `tinydb/operations.py` and had no acceptance-criteria section. The check stopped the run. 26,203 tokens.

Seeded reviews, blind and trace: [44877742774](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44877742774). All ten raw verdicts were REQUEST_CHANGES. An earlier attempt, [44877583412](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44877583412), died on `git diff master` before the model ran, because it executed the harness copy on the seed branch.

Seeded pull requests: [#7](https://github.com/Gaurav7888/autose-a3-tinydb/pull/7) good, [#8](https://github.com/Gaurav7888/autose-a3-tinydb/pull/8) bool-bug, [#9](https://github.com/Gaurav7888/autose-a3-tinydb/pull/9) dependency, [#10](https://github.com/Gaurav7888/autose-a3-tinydb/pull/10) noop, [#11](https://github.com/Gaurav7888/autose-a3-tinydb/pull/11) lying-test.

## Runs that are not results

These failed before a model judgement, or were cancelled by GitHub's pending-run rule. They are not counted in the pass rates.

- [44811701317](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44811701317) workflow file rejected on push. An unquoted colon made the YAML invalid.
- [44812492322](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44812492322), [44812505951](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44812505951), [44812517076](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44812517076) cancelled while pending. See ADR-011.
- [44812997215](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44812997215) and [44876427082](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44876427082) review jobs died on `gh` or `git diff` before the model.
- [44876435019](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44876435019) and [44876442498](https://github.com/Gaurav7888/autose-a3-tinydb/actions/runs/44876442498) requirements calls rejected because the stored OAuth token had been revoked. They were rerun.
