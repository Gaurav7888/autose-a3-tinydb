---
name: requirements-specification
description: >-
  Turns a vague or incomplete software problem statement into a reviewable
  requirements specification with traceable identifiers, separated assumptions,
  open questions, and a validation verdict. Use when the user asks for a
  software requirements specification, SRS, requirements analysis, or to turn
  an idea, brief, or stakeholder notes into testable requirements. Does not
  implement the system. Applies to any software domain.
---

# Requirements specification

Produce a requirements specification. Do not implement the system, choose a stack, or design an architecture.

**Prime rule.** A requirement is confirmed only when a supplied source states it. Memory, domain habit, and tool results are not sources. Never promote an assumption, inference, or external definition to a confirmed requirement. If a fact is missing, record a question. If two statements conflict, keep both and mark the conflict. Do not pick a winner and do not average them.

## Purpose and scope

**Objective.** Extract what the sources actually say, separate it from inference and unresolved uncertainty, and emit a specification a reviewer can check before anyone writes code.

**Intended users.** A software agent, followed by the stakeholder or analyst who reviews the draft. The skill is not a stakeholder and must not role-play one.

**Invoke when** the user supplies a software idea, brief, or stakeholder statements and wants requirements, an SRS, gap analysis, or an implementation-readiness judgment.

**Do not invoke** for implementation, code review, test-code generation, project costing, scheduling, or marketing copy. If the user asks to build the system, write the specification first and stop.

**Boundaries.** Domain-independent. Do not apply a hidden domain pack (login, CRUD, HIPAA, payments, mobile, Kubernetes, Indian law, or any other) unless a source states that obligation. A place name, a buzzword, or "enterprise" does not import a regulation or a product shape.

**Out of scope for the artefacts.** Screens, schemas, APIs, technology choices, and effort estimates. Mention them only as open questions when the source forces the topic and does not decide it.

## Inputs

**Required.** One problem statement: the text the user wants analysed. If it is missing or empty, do not interview yourself. Emit the three artefacts with document verdict `BLOCKED` and a single blocking question asking what software behaviour is wanted.

**Optional.** Named stakeholder statements (`SH-n`, author, text); a glossary the user marks as confirmed; prior specification text; an output directory; a note that no human is available.

**Missing information.** Record an open question. Continue. Do not fill the gap with a plausible feature.

**Ambiguity.** If one span has two readings that would change a test, write both readings. Do not choose the more common reading.

**Conflict.** If two spans cannot both be true, create a conflict record. Keep both spans as stated. Mark every requirement that depends on either span as not ready.

**Unavailable stakeholders.** Record `STAKEHOLDER_UNAVAILABLE`. Do not invent their answers. The draft is still delivered, with those questions unresolved.

**Human in the session.** Put blocking questions in the register. Also ask at most seven of them at the end of the reply, highest impact first. If the user said to work only from the brief, do not wait for answers; deliver the draft and keep the questions in the register.

## Analysis

### Freeze and segment

Copy each source verbatim into the source register with id `SRC-n`. Split it into atomic spans `ST-n`. A span is one claim. Do not rewrite it yet. Marketing sentences stay in the register so coverage can be checked.

### Disposition

Assign every `ST-n` exactly one disposition:

- `requirement` — a behaviour, quality, or constraint the source obliges
- `goal` — a desired quality with no measure, scope, or condition
- `non-requirement` — novelty claims, slogans, motivation, examples that are not obligations
- `conflict-member` — also used when the span is one side of a conflict
- `duplicate`

The person who requests the system is stakeholder `SH-1`, not a user, unless the text says they use or operate it.

### Quarantine

These words are goals, not requirements, until the source also states a scope, a condition, and a measure: autonomous, fully autonomous, intelligent, smart, robust, scalable, enterprise-grade, seamless, intuitive, easy, fast, secure, private, privacy-preserving, sovereign, reliable, modern, user-friendly, flexible, powerful, real-time, high-quality, comprehensive, end-to-end, world-class, first, best.

Deployment words (self-hosted, cloud, on-prem, local-first, offline-first, air-gapped) are constraints only when the source states who operates the system, where it runs, and what network assumption is in force. Otherwise they are goals plus questions.

A place or market claim ("India's first", "for hospitals") does not create a legal, language, or hosting requirement. Record a question if jurisdiction might matter. Do not import a statute from memory.

### Record types

Use these ids. Never renumber; retire a bad id as `REJECTED`.

| Id | Holds | Ready allowed? |
| --- | --- | --- |
| `ACT-n` | Actor. Status `stated` only if the source names the role | No |
| `G-n` | Quarantined goal | No |
| `FR-n` | Functional requirement: behaviour under a condition | Only if stated and testable |
| `NFR-n` | Quality with a scale and a threshold | Only if stated and testable |
| `CON-n` | Constraint the source imposes (policy, capacity, exclusion) | Only if stated and testable |
| `ASM-n` | Assumption. Not a requirement | No |
| `DEP-n` | Dependency on an external system the source names | No |
| `RSK-n` | Risk caused by a gap, conflict, or unbounded claim | No |
| `OQ-n` | Open question, with why it blocks or not | No |
| `CF-n` | Conflict between span ids | No |
| `AC-n` | Acceptance check for one requirement | Tied to that requirement |
| `EV-n` | External evidence from a tool call | No |

Epistemic status on every `FR`, `NFR`, `CON`, and `ACT`: `stated`, `inferred`, or `external`.

- `stated` — the span asserts it. Include a short quote.
- `inferred` — not written. Name the spans and the rule. Never ready.
- `external` — taken from an `EV` record. Never ready. Use it to write questions, not features.

### How to write a requirement

Use: When `<condition>`, the system shall `<observable response>`.

Split compound sentences. An unresolved sibling does not block a sibling that is independently testable.

Formalise ordinary comparatives without adding a new obligation: "exceeds" means strictly greater than; "more than N minutes" means a duration strictly greater than N; "within N" means a duration less than or equal to N. Put that formalisation in the requirement and keep the quote. If the source uses a vague quantity ("about", "around", "quickly"), do not formalise; open a question.

Do not invent data fields, channels, roles, or error behaviour. A descriptive fact becomes a constraint only when the source states an obligation. Adding a test detail the source does not contain, such as a browser rule or a capacity limit, is an inference and cannot be ready. If the verb is present but the observable result is not, status stays `stated` and readiness stays `needs_clarification`.

### Actors and boundary

List an actor only when the source names the role. If the system boundary is unclear, say so. Unknown users are questions, not actors.

### Conflicts

Quarantine does not erase a span. Flag a pair when both cannot hold, including a quarantined goal against a concrete obligation:

- two numbers for the same obligation
- two cardinalities for the same role
- a duty to work with no network and a duty to fail when a remote service is unreachable
- opposite permissions for the same actor

Do not resolve the conflict.

### Assumptions, dependencies, risks

An assumption explains a hypothesis you refused to treat as fact. Dependencies exist only for systems the source names. Risks must cite a gap, a conflict, or an unbounded claim. Do not add market or schedule risks from general knowledge.

### Acceptance criteria

For a candidate ready requirement, write a check a tester can run without asking a new question: setup, stimulus, observable outcome, and at least one negative case when a boundary was formalised. If any of those needs a missing fact, the requirement is not ready and the acceptance criterion is `blocked`.

### Readiness of one requirement

Set `ready` only when all of these hold. Otherwise `needs_clarification`, `blocked`, or `rejected`.

1. Status is `stated`.
2. It is not a member of an open conflict.
3. Condition and observable response are both present.
4. A tester can execute the acceptance criterion without a new question.
5. No blocking question is a dependency of this item.
6. The text contains no unqualified quarantine word.
7. It does not demand an unbounded property (perfect, fully, zero latency, complete autonomy, any model that will ever exist).

`unspecified` priority is allowed and does not block readiness. Do not invent MoSCoW or numeric priority.

### Document verdict

- `BLOCKED` — the input is empty, or no behaviour was stated, or a conflict covers the primary behaviour.
- `PARTIAL` — at least one requirement is `ready`, and a blocking question or a non-ready core goal remains.
- `READY_FOR_IMPLEMENTATION` — every in-scope requirement is `ready`, no open conflict, no blocking question.

A single peripheral `ready` item does not lift a conflict on the primary behaviour out of `BLOCKED`.

## Workflow

Copy this list and complete it in order. Do not skip ahead to fill a later section with invention.

1. Freeze sources. If the required statement is missing, emit the three artefacts and stop.
2. Segment into `ST-n` and dispose every span.
3. Quarantine undefined quality and deployment words into goals.
4. Name only stated actors. Record missing users as questions.
5. Draft `FR`, `NFR`, and `CON` items. Mark epistemic status on each.
6. Search the draft for conflicts. Link them with `CF-n`.
7. Consult the Fetch MCP for an undefined technical term that the source uses as an obligation and that a public definition could turn into questions. Skip the tool for missing product decisions (who the users are, what the features are). See MCP below. Cap: three terms, two URLs per term.
8. Re-read the draft. Downgrade anything the tool tempted you to add as a confirmed requirement. Add questions instead.
9. Write acceptance criteria. Apply the readiness gate per item.
10. Write assumptions, dependencies, and risks from the gaps you actually have.
11. Run the validation checks. If a check fails, revise the artefacts once. If the only fix is to invent a fact, downgrade the item instead.
12. Set the document verdict from the item statuses. Then stop. Do not implement.

## Outputs

Write three Markdown files in the output directory (default `./requirements/<slug>/`). Slug: lowercase hyphenated system name if the source names one, otherwise `untitled-system`.

| File | Contents |
| --- | --- |
| `<slug>-srs.md` | The specification |
| `<slug>-register.md` | Assumptions, questions, conflicts, evidence |
| `<slug>-validation.md` | Check results and verdict |

### `<slug>-srs.md`

```markdown
# Requirements specification: <name or "Untitled system">
Status: DRAFT
Document verdict: BLOCKED | PARTIAL | READY_FOR_IMPLEMENTATION

## 1. Sources
SRC-n, stakeholder, verbatim text.

## 2. Problem statement
Verbatim. Do not improve the wording.

## 3. Boundary
What is inside the system, what is outside, and what is unknown. Unknown stays unknown.

## 4. Actors
ACT-n, stated role, quote, status. If none, write "No actor is stated."

## 5. Goals (not requirements)
G-n, quote, why it is not testable, linked OQ ids.

## 6. Functional requirements
FR-n. Status. Readiness. Quote. Statement. Source spans. Blocking questions.

## 7. Non-functional requirements
NFR-n, same fields. If none qualify, write "No testable non-functional requirement is stated."

## 8. Constraints
CON-n, same fields.

## 9. Dependencies
DEP-n or "None stated."

## 10. Acceptance criteria
AC-n linked to one requirement, or blocked.

## 11. Traceability
ST-n, disposition, requirement ids or the reason it is not a requirement.

## 12. Verdict
One paragraph. State what is ready, what is not, and that this document does not authorise implementation of unresolved items.
```

### `<slug>-register.md`

```markdown
# Assumptions and open questions: <slug>

## Assumptions
ASM-n. Hypothesis. Why it was not promoted. Confirming stakeholder.

## Open questions
OQ-n. Question. Blocking: yes or no. What it blocks. Options only if the source already contains them. Do not recommend an option.

## Conflicts
CF-n. Span A. Span B. Requirements blocked. No resolution.

## External evidence
EV-n. Term. URL. Tool. Status: SUCCESS or TOOL_FAILURE. Paraphrase of at most 80 words. Questions created. Confirmation: "Not a requirement until a stakeholder confirms it applies."
```

### `<slug>-validation.md`

```markdown
# Validation summary: <slug>
Document verdict: ...
Checks: V1–V12, each PASS or FAIL with the offending ids.
Ready ids:
Not-ready ids and the failed gate:
Human intervention required: yes or no, and why.
```

## Validation

Run every check. A FAIL means the specification is not validated until it is revised or the offending item is downgraded.

| Id | Question | Fail action |
| --- | --- | --- |
| V1 | Is every `ST-n` in the traceability table? | Add the missing disposition |
| V2 | Does every `FR`/`NFR`/`CON` cite a span, or an inference rule? | Add the citation or delete the item |
| V3 | Is any `inferred` or `external` item `ready`? | Downgrade it |
| V4 | Does a `ready` item contain an unqualified quarantine word? | Downgrade to goal or question |
| V5 | Does every `ready` item have condition, response, and a runnable check? | Downgrade |
| V6 | Does every `CF-n` block the requirements it touches? | Block them |
| V7 | Are all ids unique? | Rename duplicates; do not reuse retired ids |
| V8 | Is any `ASM-n` copied into a requirement as if it were stated? | Remove the requirement or mark `inferred` |
| V9 | Can each `ready` quote be found in a source? | Downgrade |
| V10 | Is any unbounded claim `ready`? | Downgrade |
| V11 | Does every `external` item cite an `EV` with status `SUCCESS`? | Downgrade; a failed fetch is not evidence |
| V12 | Does the document verdict match the item statuses? | Recompute the verdict |

Completeness is V1 plus an explicit "not stated" for users, capabilities, environment, and security whenever those are absent. Consistency is V6. Traceability is V2 and V9. Feasibility is V10. Testability is V4 and V5.

An item is ready for implementation only if its readiness is `ready` and V3–V6, V9, and V10 pass for it. The document authorises implementation of the whole system only when the verdict is `READY_FOR_IMPLEMENTATION`. Any other verdict means the agent must not start building.

## Failure handling

**Ask** when a human is present and a blocking question would change the primary behaviour. Ask those questions. Do not pause the draft: deliver it in the same turn with the questions recorded.

**Document, do not ask,** when the human is absent or told you to use only the brief.

**Do not silently convert** an unsupported assumption into a confirmed requirement. This includes the case where you are confident you know what the stakeholder meant.

**Tool failure.** Retry the same call once. If it fails again, you may try one different public URL for the same term. If that fails, write `EV` with `TOOL_FAILURE` and leave the term unresolved. Do not replace the page with memory and label it `external`.

**Irrelevant tool result.** Ignore it. Record that the page did not define the term. The question stays open.

**Tool result conflicts with a stated span.** Keep the span. Add a note that the public definition differs. The stakeholder must choose. Do not edit the stated text to match the page.

**Unverified claims on a page.** They stay `external`. They do not become `stated`.

**Human intervention is required** when a conflict covers the primary behaviour, when external evidence contradicts a stated obligation, when the input is not a software problem, or when the user asks you to invent the product. Say so in the validation file. Do not paper over it with a plausible specification.

**Revision limit.** One validation repair pass. After that, ship `DRAFT` and list the failed checks.

## MCP

Use the public Fetch MCP server to retrieve a definition you do not get to invent.

- Source and docs: [Fetch MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) (`mcp-server-fetch`).
- Why this server: requirements analysis needs primary text for undefined technical terms. Fetch returns page content. It does not decide whether that content is in scope for this stakeholder. That matches the prime rule.
- Why not a search-from-memory step: a remembered definition is not evidence and must not be written as an `EV` record.

**Discover.** Prefer a configured MCP server that exposes a tool named `fetch`. Otherwise start `python -m mcp_server_fetch` or `uvx mcp-server-fetch` over stdio.

**Invoke.**

1. Initialise an MCP session.
2. `tools/list`. Confirm a tool named `fetch`.
3. `tools/call` with `url` (required), `max_length` 5000, `start_index` 0, and `raw` false.
4. Timeout 30 seconds. Retry the same arguments once on timeout, connection error, robots refusal, or HTTP error.
5. If the response includes a truncation notice, call again with the `start_index` it names. Continue for at most four chunks. Stop early once the defining passage, including every enumerated item, is fully in hand. A heading that names a list is not the list.
6. Ignore non-protocol text on stdout. A call is `SUCCESS` only when the tool returns page text for the requested URL. Paraphrase that text in at most 80 words and keep the URL.

**Consume.** Create `EV-n`. For each property in the paraphrase that the stakeholder did not already state, add an `OQ-n`: "Does this project include `<property>`?" Set confirmation to not-a-requirement. Do not add an `FR` or `NFR` from the page.

**Do not fetch** to discover users, feature lists, or prices. Do not fetch more than three terms per specification.

**Boundaries for any specification.**

- Established from the problem statement: only spans you can quote.
- Supportable by Fetch: the public meaning of a term, and the questions that meaning creates.
- Still requires the stakeholder: which of those meanings apply, plus every product decision the text does not contain.

## Examples

**Quarantine.** Source: "The app should be easy and fast." Dispose both as goals. Open questions ask for the task, the user, and the latency bound. Write no `NFR`. Readiness of the document is `BLOCKED` if nothing else is stated.

**Conflict.** Source: "Appointments are 15 minutes. Appointments are 30 minutes." Create `CF-1` on those spans. Do not specify 15, 30, or 22.5. Both booking rules are `blocked`.

**Tool result.** Source says "local-first" and nothing about offline work. Fetch returns a definition that includes offline work. Record `EV-1` and ask whether offline work is in scope. Do not add "the system shall work offline" as `stated` or `ready`.
