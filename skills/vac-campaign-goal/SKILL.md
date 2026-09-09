---
name: vac-campaign-goal
description: Generates the campaign configuration for a voice-agent build — campaign-goal.md (the campaign goal definition, i.e. the campaigns.campaign_goal free-text field) plus call-outcomes.json (the typed campaigns.call_outcomes list). Runs at step 9 of the VAC pipeline (per the SSOT in PIPELINE.md), after vac-task-extraction. Both artifacts are derived from the agent's briefing.md Call Objectives and are what the campaign platform uses at runtime to classify each call's outcome (success / lead) and to feed the goal context into every post-call analysis. Use whenever building a voice agent and the campaign's goal definition + outcomes are needed, or whenever the user asks to create a goal definition, campaign goal, call outcomes, success definition, outcome types, or the campaign platform's campaign-goal/outcome config for an agent — even if they only say "generate the goal" or "outcomes for agent X" without naming the fields. English output artifacts.
---

# VAC Campaign Goal

Produces the two campaign-config artifacts for a voice-agent build:

- **`campaign-goal.md`** — the copy-paste campaign goal definition. Goes into your campaign platform's goal field.
- **`call-outcomes.json`** — the typed outcome list. Goes into your campaign platform's outcomes field.

## Prerequisites (input check)

Before starting, check that these files exist in the agent directory (`../voice-agents/<agent>/`):

| File | Comes from | If missing |
|---|---|---|
| `briefing.md` | `vac-intake` (step 1) | Run `vac-intake` first |

If an input is missing, do NOT improvise and do NOT carry on with placeholders: name the missing upstream step and ask the requester or workspace admin whether it should be run now. (On top of that, this skill enforces two MUST-HAVE preconditions on the briefing's content, see below.)

Both are derived from the same source as `vac-task-extraction`: the **Call Objectives** in `briefing.md`. This skill is the sibling of `vac-task-extraction` — task-extraction writes the post-call *task* prompt, this one writes the *goal + outcomes* that the campaign platform uses to score whether the call succeeded.

## Pipeline Position

Step 9 (see `PIPELINE.md`) — runs after `vac-task-extraction` (step 8). It needs only `briefing.md` as input, so it can technically run any time after the briefing is finalized; the canonical position is step 9 so both campaign-config artifacts (task-extraction prompt + goal/outcomes) sit together and any live-test findings from step 7 are already folded into the briefing. Input: `briefing.md`. Output: `campaign-goal.md` + `call-outcomes.json` in the agent's build directory.

## What you're building, and how the platform uses it at runtime

The goal is NOT a display string. Both artifacts drive live behavior in your call-processing pipeline. Write them knowing exactly how they are consumed — otherwise you produce a goal the classifier cannot act on.

- **`campaign_goal` → the goal-outcome classifier.** After each answered call, the platform runs an LLM structured call (`GoalOutcomeAnalysis`) that receives `campaign_goal` and the `call_outcomes` labels, and picks the single matching outcome (or a `NO_MATCH` sentinel). The chosen outcome's `type` is then mapped by `OutcomeDeterminationService` to the call's business result: `success → Converted / is_successful=true`, `failure → NotConverted / false`, `follow_up → Undetermined / null`. **So the goal text is the yardstick the classifier reads to decide success/lead.** It must state, in plain terms, what a successful call is, what a failed call is, and what merely warrants follow-up.
- **`campaign_goal` → context for every analysis.** The goal is also injected as a `<campaign><goal>…</goal></campaign>` block into the user prompt of *all* post-call analyzes (task extraction, call summary, voicemail, callback, opt-out). So it doubles as the shared "why are we calling" context. Keep it truthful and self-contained — no goal → the block is dropped and every analysis loses that context.
- **`call_outcomes` labels → the classifier's enum.** The classifier matches the transcript against the exact `label` strings. Labels must be short, mutually distinguishable, and cover the real conversation endings **of calls that were actually conducted** (see SCOPE below — no mailbox/not-reached/opt-out labels). A `NO_MATCH` sentinel is built in, so you never need an "Other" catch-all.

Because a below-threshold or `NO_MATCH` classification falls through to `Undetermined`, the goal + outcomes only pay off when they are specific. A generic goal produces mushy classifications.

## SCOPE — only actually-conducted conversations (BLOCKING boundary)

`campaign_goal` and `call_outcomes` describe the **result of a conversation that actually took place**. They are NOT a call-disposition enum. Everything that is a connection state rather than a conversation result is handled deterministically in the campaign platform (code/flags/data_collection), never by the LLM goal-outcome classifier — so it must **never** appear as an outcome and must **not** be framed as a failure case in the goal text.

**Never generate these as outcomes (the platform handles them deterministically):**

| Excluded ending | Why it's out of scope |
|---|---|
| Mailbox / answering machine | No conversation happened; the platform marks the lead for retry programmatically |
| Not reached / no answer | Connection state, not a conversation result |
| Busy | Connection state |
| Technical error / call dropped / abort | No usable conversation; handled by the telephony/pipeline layer |
| Opt-out ("do not call again") | Captured deterministically (data_collection flag → contact is blocked), independent of the outcome label |

So the goal text does **not** get a "NOT successful: voicemail / not reached / call dropped / opt-out" tail, and `call_outcomes` gets **no** `Voicemail / not reached` and **no** `Opt-out` entry. The `failure` type is reserved for a **real negative conversation result** — a call where a person was spoken to but no need exists (e.g. "not relevant at the moment", "no need", "already solved another way"). There is always at least one such genuine-conversation failure; that is what satisfies the "≥ 1 failure" contract, not a mailbox/opt-out placeholder.

## MUST-HAVE Preconditions (BLOCKING)

This skill needs a real definition of success to produce meaningful outcomes. If either is missing AND cannot be reasonably inferred from the briefing, **STOP the run** and ask the user. Guessing outcomes produces a classifier that mislabels every call.

| # | Precondition | Where it usually lives | Why it's MUST-HAVE |
|---|---|---|---|
| 1 | **Agent Primary Goal** | `briefing.md` → `primary_goal` / "Call Objectives" / `use_case_description` | Without it there is no yardstick — the goal text collapses to a generic restatement of "make a call" |
| 2 | **Expected Conversation Outcomes** | `briefing.md` → `success_metrics` / `secondary_goals` / a success-vs-failure list | Without it you cannot split success / failure / follow_up — the whole `call_outcomes` list is a guess |

### How to detect missing MUST-HAVEs
For each: look under the typical section names, then adjacent context (primary/secondary goals, success metrics, no-gos that imply failure endings). If genuinely nothing is there: **block**.

### Blocking message format
When you block, output this to the user (write no file):

```
SKILL BLOCKED — MUST-HAVE information missing

The following details are missing from the briefing and cannot be inferred:
- [List each missing precondition by number and name]

What to do:
- [Concrete instruction per missing item — which briefing section to fill, or which info to provide inline]

This skill produces no output until that information is available.
Reason: without a real definition of success, the platform misclassifies every call.
```

---

## Field contract (do NOT invent shapes — verify against code before shipping)

Both fields are validated by `ValidatesCallOutcomes` (used by `Store`/`UpdateCampaignRequest`) and read by `GoalOutcomeAnalysis` + `OutcomeDeterminationService`. This table is the complete, closed contract.

| Field | Type / limit | Notes |
|---|---|---|
| `campaign_goal` | string, **max 5000 chars**, nullable | free text; API/UI-settable the normal way |
| `call_outcomes` | array, **max 10 items**, nullable | typed object format (below) |
| `call_outcomes[].id` | **valid UUID**, required | NOT a slug — `uuid` rule rejects `opt_out`-style ids |
| `call_outcomes[].label` | string, **max 100 chars**, required | the exact string the classifier matches |
| `call_outcomes[].type` | enum, required | one of `success` \| `failure` \| `follow_up` — no other value |
| `needs_outcome_review` | boolean | **must be `false`** for classification to run (`isClassificationActive`) |

**Hard constraints enforced by the validator:**
- At least **one `success` AND one `failure`** outcome, or the platform rejects the whole set.
- At most **10** outcomes total.
- Classification is only *active* when outcomes are non-empty, at least one has a `type`, AND `needs_outcome_review === false`. A freshly authored, deliberate set → emit `needs_outcome_review: false`.

**UUIDs:** generate real ones, do not hand-fake. Cross-platform (works everywhere): `python3 -c "import uuid; [print(uuid.uuid4()) for _ in range(10)]"` (one per outcome). macOS alternative: `uuidgen` (lowercase it). Slugs will fail validation on deploy.

**Deploying (not this skill's job):** both fields are API/UI-settable (unlike `extraction_schema`). Deploy via the normal campaign update or the campaign API skill. This skill only writes the artifacts; it does not touch the live campaign.

---

## Deriving `campaign_goal` (the goal definition text)

Write it in **English**, as prose the classifier and the follow-up team both read. Target well under 5000 chars — a tight goal beats a wall of text. Structure (not rigid; adapt to the agent):

1. **One opening paragraph** — who calls whom, in whose name, with what purpose, and the hard no-gos that define the agent's lane (e.g. "does not sell, does not quote prices"). Pull this from `use_case_description` + `no_gos`.
2. **"A call is SUCCESSFUL if …"** — a bulleted list of the concrete success conditions, drawn from `primary_goal` + `success_metrics`. Each bullet is one recognizable conversation result.
3. **"Counts as a valid result and is NOT scored as a failure …"** — the clean-negative *conversation* cases (not relevant, already covered / fixed partner). These matter: the briefing usually says a clean negative is a valid result, and the classifier needs to know they are real `failure`/`follow_up` outcomes, not junk. Do NOT list Opt-out here — it is handled deterministically in the campaign platform (see SCOPE).
4. **"A conversation that took place is NOT successful when …"** — the dead ends *within a real conversation*: a person was spoken to but no usable info, no responsible contact, no contact way, and no acknowledged need. Do NOT add mailbox, not-reached, busy, abort, or opt-out tails — those are out of scope (SCOPE section) and the platform handles them deterministically. Optionally open the goal with one sentence stating that the definition applies only to conducted conversations.

The goal text and the outcome labels must be **consistent**: every success bullet should correspond to a `success` (or `follow_up`) outcome, every dead-end to a `failure` outcome. Write the goal first, then derive the outcomes from it — they are two views of the same success model.

## Deriving `call_outcomes` (the typed list)

Turn the goal's success model into discrete, matchable outcomes. Rules:

- **One outcome per recognizable conversation ending**, phrased as the label the classifier will match (≤100 chars, English, concrete). Prefer the caller-visible result ("Contact person + way to reach them secured") over internal jargon.
- **Type mapping:**
  - `success` — the primary goal is reached (usable need/market info captured, responsible contact + contact way secured).
  - `follow_up` — inconclusive but a next step exists (way to the right person obtained, "of interest later", callback window, info-by-email requested, fixed-partner-but-open).
  - `failure` — a clean, valid negative **conversation result** (not relevant at the moment, no need, already solved another way). Clean negatives are `failure`, not something to omit — the team still needs them recorded. Do NOT create `failure` outcomes for mailbox / not-reached / busy / abort / opt-out — those are connection states / deterministic flags handled by the campaign platform, not conversation results (see SCOPE).
- **Coverage, not exhaustiveness.** Cover the *conversation* endings the briefing actually implies. Do NOT pad to 10. Do NOT add an "Other"/"Unclear" outcome — `NO_MATCH` handles the unmatched case in the campaign platform.
- **Respect the hard constraints:** ≤10 total, at least one `success` and one `failure`. The mandatory `failure` must be a genuine-conversation negative ("no need" / "not relevant at the moment"), never a mailbox/opt-out placeholder. If your natural set has no clean `failure` (rare), re-read the briefing's no-gos and refusal handling — there is almost always a "no need" / "not relevant" ending.
- **IDs:** one fresh UUID per outcome (see contract). Order the array success → follow_up → failure for human readability; order does not affect runtime.

Worked examples across agent types (cold outreach, job ads): `references/outcome-examples.md`. Read it when the mapping for a given ending is unclear.

---

## Output: `campaign-goal.md`

**The file contains ONLY the bare goal definition text — copy-paste ready** into your campaign platform's goal field. It starts directly with the first paragraph of the goal. Do NOT add a document title, a metadata block, an "Applied sources" table, or any notes — everything that is not the goal text itself goes into the Active Report (chat). No `#` headlines are needed; the goal is prose with inline "SUCCESSFUL …" / "NOT successful …" cue phrases (bold or plain, your call), matching the structure above.

## Output: `call-outcomes.json`

A JSON array of typed outcome objects, exactly matching the LOCKED contract. Copy-paste / API-ready. Shape:

```json
[
  { "id": "3f2a…-uuid", "label": "Needs/market info captured",                 "type": "success" },
  { "id": "9b71…-uuid", "label": "Contact person + way to reach them secured", "type": "success" },
  { "id": "c40e…-uuid", "label": "Route to the right person obtained",         "type": "follow_up" },
  { "id": "0d55…-uuid", "label": "Not relevant at the moment",                 "type": "failure" }
]
```

(No `Opt-out` / `Mailbox` entries — those are out of scope; the platform handles them deterministically. The single `failure` here is a real negative conversation result.)

Use real UUIDs (never the `3f2a…` placeholders above). Emit ONLY the array — no wrapping object, no `needs_outcome_review` key inside the file (that boolean is a campaign column set at deploy time, reported in chat, not part of the outcomes array).

---

## Active Reporting (after writing the files)

After writing both files, report to the user with this structure:

```
Skill complete: campaign-goal.md + call-outcomes.json written to <path>

Goal definition:
- Primary goal: [briefing source — e.g. "primary_goal: vacancy status + relevance"]
- Length: [N chars / 5000]

Call Outcomes (N/10):
- success: [count] · follow_up: [count] · failure: [count]  (min. 1 success + 1 failure: satisfied)
- [one line per outcome: label → type]

Deploy note:
- When setting up the campaign, needs_outcome_review = false, otherwise classification stays inactive.
- campaign_goal + call_outcomes are API/UI-settable (via the campaign API or the campaign UI).

Notes:
- [Anything derived vs. defaulted, or briefing gaps, e.g. "Briefing named no follow-up cases — only success/failure generated"]
```

This report is the ONLY place the meta lives — it stays out of the files so both are copy-paste ready. Reporting in chat makes derivation choices visible without polluting the artifacts.

---

## Quality Gate

Before finishing, verify:
- [ ] Both MUST-HAVE preconditions satisfied (otherwise: block, write nothing)
- [ ] Goal text defines success, valid-negative, AND dead-end cases — not a generic restatement
- [ ] Goal text ≤ 5000 chars, English, self-contained (readable with no other context)
- [ ] Outcomes derived FROM the goal — every success bullet has a matching outcome, every dead-end a `failure`
- [ ] ≤ 10 outcomes; at least one `success` and one `failure`
- [ ] Every `type` is exactly `success` / `failure` / `follow_up`
- [ ] Every `id` is a real, valid UUID (not a slug, not a placeholder)
- [ ] No "Other"/"Unclear" catch-all outcome (NO_MATCH covers it)
- [ ] No out-of-scope outcomes: NO `Voicemail / not reached`, `Busy`, `Call dropped`, `Opt-out` labels (the platform handles these deterministically); the mandatory `failure` is a real negative conversation result
- [ ] Goal text has no "voicemail / not reached / call dropped / opt-out" failure tail
- [ ] `call-outcomes.json` is a bare array, no wrapping object, no `needs_outcome_review` inside it
- [ ] `campaign-goal.md` is bare goal text — no title, no meta table, no notes
- [ ] `needs_outcome_review = false` deploy note given in the Active Report
- [ ] Active report sent after writing
