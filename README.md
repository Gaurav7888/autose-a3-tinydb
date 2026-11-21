# AutoSE assignment 3

Gaurav Sarkar, roll number 2025701012.

## Fork

- Upstream: https://github.com/msiemens/tinydb
- Pin: `edff96aeb2616402e9489d46e90a592c05565621` (TinyDB 4.9.0). `master` on this fork starts at that commit.
- This fork: https://github.com/Gaurav7888/autose-a3-tinydb

## Models

| Role | Model |
| --- | --- |
| Analyst (requirements and design) | `claude-haiku-4-5` |
| Builder | `claude-sonnet-4-6` |
| Reviewer | `claude-sonnet-4-5` |
| Monolith experiment | `claude-sonnet-4-6` |

The workflow calls the Anthropic Messages API. `ANTHROPIC_AUTH_TOKEN` is a repository secret. An `sk-ant-api...` key is sent as `x-api-key`. Any other token, including a Claude Code OAuth token, is sent as a bearer token with the `oauth-2025-04-20` beta header. `PR_TOKEN` is a maintainer token used only to push the issue branch and open the pull request. The review job does not receive it.

Recorded stage tokens, from the uploaded `usage.json` files, are 452,567. Review calls are extra and were not in those files. There is a hard stop at 500,000 input plus output tokens inside one stage process. Results and run links are in `results/`. `demo.mp4` walks through issue 3, run 44876587072, from the issue text to the posted review. The pages are the links in `results/runs.md`.

## How to start a run

A collaborator with write access does one of these on this repository, not on upstream:

- Add the label `autose` to an issue.
- Comment `/autose` as the first line of an issue comment. That starts the full pipeline.
- Comment `/autose` as the first line on an open pull request. That starts a review only.

`master` is protected. The workflow never merges. It pushes `autose/issue-N` or `autose/monolith-issue-N` and opens a pull request.

A second trigger waits, then stops if that issue already has an open AutoSE pull request. If a run dies and leaves the label `autose-running`, remove the label before starting again.

To rerun one issue by hand:

```bash
gh workflow run autose.yml -f issue_number=1 -f variant=split
```

`variant=monolith` is the experiment in `experiment/variants.md`, not the default.

The reviewer experiment, after the seeded pull requests exist:

```bash
gh workflow run autose-experiment.yml
```

## Layout

`architecture/` is the design, committed before the agent code. `workflow/` is the harness and a copy of the workflow files. The files Actions runs are in `.github/workflows/`. Hidden tests are in `experiment/hidden_tests/` and are not on the agent's tool allowlist. The build and review jobs also delete that directory from the working tree before the model starts.

## AI assistance

A coding agent in Cursor drafted the workflow, the checkers, the report and the ADR text from the A1 skill and the A2 TinyDB study. The runs linked from `results/runs.md` are real Actions runs. The ADRs were checked against those runs, including the ones that came out the other way.
