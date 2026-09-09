---
name: vac-review
description: Review voice agent prompts against a 20-dimension scoring rubric. Use after prompt writing to score quality and identify issues. Iterates up to 3 times, then escalates to a human reviewer (the requester). Minimum score 4.0/5.0 required.
---

# VAC Review

Score the prompt against the rubric. Iterate or escalate. Output: `review-log.md`.

> **Prompt architecture foundation:** `../../VOICE-AGENT-PROMPT-ARCHITECTURE.md` — the overarching SSOT
> for rule-vs-goal steering. Pipeline mechanics stay in `PIPELINE.md`.

## Prerequisites (input check)

Before starting, check that these files exist in the agent directory (`../voice-agents/<agent>/`):

| File | Comes from | If missing |
|---|---|---|
| `briefing.md` | `vac-intake` (step 1) | Run `vac-intake` first |
| `research.md` | `vac-research` (step 2) | Run `vac-research` first |
| `conversation-design.md` | `vac-design` (step 3) | Run `vac-design` first |
| `prompt.md` | `vac-prompt` (step 4) | Run `vac-prompt` first |
| `config.json` | `vac-prompt` (step 4) | Run `vac-prompt` first |
| `example-variables.md` | `vac-prompt` (step 4) | Run `vac-prompt` first |
| `knowledge-base.md` | `vac-knowledge-base` (step 3b) | KB agents only; run `vac-knowledge-base` first |

If an input is missing, do NOT improvise and do NOT carry on with placeholders: name the missing upstream step and ask the requester or workspace admin whether it should be run now.

## Process

1. Read all artifacts: `briefing.md`, `research.md`, `conversation-design.md`, `knowledge-base.md` (if present), `prompt.md`, `config.json`, `example-variables.md`
2. Score each of 20 dimensions (1-5 scale)
3. Write detailed feedback for any dimension < 4.0
4. If overall score >= 4.0 and no dimension < 3.0: **PASS** → proceed to human review (the requester)
5. If score < 4.0 or any dimension < 3.0: **REWORK** → fix and re-score
6. After 3 rework iterations: **ESCALATE** to the requester with all scores and notes

## Scoring Rubric (20 Dimensions)

### Conversation Handling (6 Dimensions)

| # | Dimension | 1 (Fail) | 3 (Adequate) | 5 (Excellent) |
|---|---|---|---|---|
| 1 | **Naturalness** | Robotic, scripted, sample-question lists | Functional, stiff | Indistinguishable from a human. Intent specs instead of sample utterances. Variation rule present. Reaction markers controlled, follow-up budget respected |
| 2 | **Phase transitions** | Abrupt, illogical | Noticeable but acceptable | Seamless, conversation-driven, exit conditions defined per phase |
| 3 | **Objection Handling** | None or aggressive | ARC present, generic | ARC use-case-specific + diagnose-first on vague/past-experience skepticism, 2-loop limit, "Schicken Sie was" recognized as a win |
| 4 | **Conversation control** | Loses control | Steers mechanically | ONE-action rule, follow-up budget, answer utilization & signals, re-engage (open question after substance), diagnose-first, non-repetition |
| 5 | **Greeting Protection** | Missing | Mentioned but vague | Complete: opener protection, interrupt handling, never restarts. "This step is important" |
| 6 | **Closing Behavior** | A plain "Tschüss" | Thanks + goodbye | Post-Close Listen Window, Close Confirmation + Final Closing, reopen limit, follow-up expectation (who gets in touch, when) |

### Prompt Quality (5 Dimensions)

| # | Dimension | 1 (Fail) | 3 (Adequate) | 5 (Excellent) |
|---|---|---|---|---|
| 7 | **Clarity** | Contradictions | Understandable, some ambiguity | Crystal clear, no ambiguity, consistency priority |
| 8 | **Consistency** | Tone/style shift | Mostly consistent | Uniform throughout, "when in doubt" fallback defined |
| 9 | **Guardrails** | Missing or patchy | Basics covered | Complete: pricing, samples, competitors, opt-out, AI, gatekeeper, commitments, escalation path |
| 10 | **Variable usage** | Hardcoded, no vars | Present, defaults missing | Smart defaults, behavior-if-empty documented, non-empty placeholders |
| 11 | **Latency optimization** | Verbose, >18,000 chars, decorative formatting | <18,000 chars, reasonably compact | <10,000 chars simple / 13,000–17,000 engaged (Answer Bank), ceiling ~18,000 (empirical on a small, fast model), measured from `# Identity` (characters, not KB), "first word fast", max 2 sentences (substantive answer ~3 + question), no ######/------  |

### Robustness (3 Dimensions)

| # | Dimension | 1 (Fail) | 3 (Adequate) | 5 (Excellent) |
|---|---|---|---|---|
| 12 | **Adaptive Modes** | No modes | One present | TIME PRESSURE + RESISTANCE + DE-ESCALATION defined, mirroring rules |
| 13 | **Edge Cases** | Voicemail/language barrier missing | One present | Voicemail + language barrier + gatekeeper rejection + external sales partners |
| 14 | **Audio Tag Governance** | Tags without rules, or missing | Tags with descriptions | Mandatory/optional moments, never consecutive, tag mapping, max 1/turn |

### Business Effectiveness (3 Dimensions)

| # | Dimension | 1 (Fail) | 3 (Adequate) | 5 (Excellent) |
|---|---|---|---|---|
| 15 | **Goal attainment** | CTA missing/weak | CTA present, generic | CTA specific, "Schicken Sie was" = win, follow-up expectation set |
| 16 | **Value Proposition** | No added value | Benefit mentioned | USP specific, social proof, niche argument |
| 17 | **Conversation opening** | Generic, no hook | Functional | Smart default for the contact person, reason for calling, gatekeeper navigation |

### Compliance & Technology (3 Dimensions)

| # | Dimension | 1 (Fail) | 3 (Adequate) | 5 (Excellent) |
|---|---|---|---|---|
| 18 | **Privacy & language** | Violations, inconsistent register, forbidden words | Basics OK | Consistent register throughout, no forbidden words, character normalization, AI disclosure |
| 19 | **Config completeness** | Missing fields, invalid JSON | All fields, defaults OK | `turn` (not `conversation`), soft_timeout 2-3s, turn_eagerness set, non-empty defaults |
| 20 | **Example Variables** | Missing | 1-2 scenarios | 3+ scenarios, smart defaults documented, edge cases, all vars covered |

## Scoring Rules

- **PASS:** Overall average >= 4.0 AND no single dimension < 3.0
- **REWORK:** Overall average < 4.0 OR any dimension < 3.0
- **ESCALATE:** After 3 rework iterations without PASS

## Behavioral Checklist (Run AFTER scoring)

In addition to dimension scoring, verify these patterns exist in the prompt:

**0a. NO sample-question lists for data-gathering phases** (Few-Shot Bias avoidance). Discovery, Implication, Fit Check use INTENT SPECS, not example utterances.
**0b. Variation rule present in Conversation Rules**: "phrase every question in your own words; never recite identical phrasings".
**0c. Reusable templates clearly marked** with `use this exact phrasing or very close`.


1. Greeting Protection
2. Post-Close Listen Window
3. Max 2 sentences per turn (substantive answers may run ~3 + a re-engaging question)
4. ONE action per turn
5. Reaction Marker Policy with frequency limits
6. Follow-up Budget (1+1)
7. ARC method with loop limit
8. TIME PRESSURE mode
9. RESISTANCE mode
10. DE-ESCALATION framework
11. Mirroring rules (what to mirror, what not)
12. Non-Repetition rule
13. Answer Utilization
14. Gatekeeper handling with "never pitch" rule
15. Discovery before pitch
16. Product USP/differentiator
17. Email/CTA capture
18. Voicemail handling (outbound)
19. Language Barrier handling
20. Guardrails section with NEVER/ALWAYS
21. AI disclosure
22. Forbidden words listed
23. Audio Tag governance (mandatory/optional)
24. Character Normalization + Echo-confirmation for irreversible data (email/phone/appointment) with OPEN re-confirmation ("passt das so?", never ja/nein); phone digit-by-digit; numbers/amounts/dates verbalized
25. Context Variables with defaults (incl. `account_agent_name` with a speakable default)
26. Warm lead variant
27. Escalation person named
28. Pricing guardrail (never name prices)
29. Samples/tasting guardrail
30. Opt-out immediate exit
31. **Outbound: first_message is empty (`""`) in config.json** — Opening greeting is in prompt under `# Opening` instead
32. **Inbound: first_message is set in config.json** with Smart Defaults for all variables
33. **All Dynamic Variables have non-empty default values** in config.json `dynamic_variable_placeholders`
34. **Outbound: `# Dialed Number` block** with `{{lead_phone_number}}` + no-invented-number rule (prevents phone hallucination; the placeholder is what forces the production dispatcher to pass the real number)
35. **Re-engage after substance**: substantive answers end with one OPEN question (never closed "Macht das Sinn?"), toward situation or next step
36. **Diagnose before you argue**: vague/past-experience objections get one open diagnostic question first, then tailored substance
37. **Signal-reading**: volunteered prior provider / budget / how-they-work explored, not plowed past; rejected frame words not reused
38. **Answer Bank** (engaged-decision-maker agents only): answer-vs-defer boundary present; substance is concise, not an unsolicited mini-pitch
39. **Trigger labels** (objection / Answer Bank) in German, handling instruction in English
40. **Knowledge base** (knowledge-base.md present): spoken paraphrasable German, question-anchored headers, guardrail-taboo content EXCLUDED (no prices/hard timelines/named customers), fact/number review flags in meta, tier-2 not duplicated in the prompt
41. **Outbound: `# TURN 1 — ABSOLUTE RULE` block** present as the FIRST prompt block (before `# Identity`), opener verbatim-identical to `# Opening`, 4 WRONG/RIGHT few-shots; Greeting Protection + Opening + Reaction-Policy + Guardrails reference it without contradiction; silence fallback framed as a follow-up, never a substitute for turn 1

Missing items = REWORK with specific fix instructions. Items 38-39 only apply to engaged-decision-maker agents; item 40 only to KB builds; item 41 only to outbound agents.

### Hard Fail Checks (instant REWORK, no scoring needed)

These are binary checks. If ANY fails, the review result is REWORK regardless of scores:

- Outbound agent + non-empty `first_message` in config.json = **HARD FAIL**
- Inbound agent + empty `first_message` in config.json = **HARD FAIL**
- Any `dynamic_variable_placeholders` value is `""` for a variable used in prompt or first_message = **HARD FAIL**
- **Few-Shot Bias detected**: prompt contains sample-question lists for Discovery, Implication, Fit Check, or any data-gathering phase (2+ similar-shape phrasings in a row that the model would treat as templates) = **HARD FAIL**. Reusable EXACT templates marked with `use this exact phrasing` are allowed and not a fail.
- **Variation rule missing**: prompt does not contain an explicit instruction to phrase questions in the model's own words and not recite = **HARD FAIL**.
- **Outbound agent without `# Dialed Number` block** exposing `{{lead_phone_number}}` (with non-empty default in config) = **HARD FAIL**. Without it the agent hallucinates the caller's number when asked, and the production dispatcher never passes the real number (only `{{...}}` placeholders enter `dispatch_variables` at schedule time).
- **Outbound agent without `# TURN 1 — ABSOLUTE RULE` block** as the first prompt block (SSOT: vac-prompt `references/universal-prompt-rules.md`) = **HARD FAIL**. Without it the model reacts to the (often STT-garbled) first user utterance instead of opening, skipping AI-disclosure/opener — verified failure mode on a small fast model (gpt-5.4-mini) (verified across two production outbound agents). The opener inside the block must be verbatim-identical to `# Opening`; a divergence between the two is itself a fail (two competing openers).
- **Hardcoded agent name instead of `{{account_agent_name}}`** = **HARD FAIL** (convention: the account agent name arrives as a dispatch variable on every call; each account has ONE name for all of its agents). Check: Identity, `# Opening`, first_message, voicemail text — everywhere `{{account_agent_name}}` as a rendered value, placeholder with a speakable non-empty default. A persona name may only appear as the placeholder DEFAULT and in docs/meta, never in the spoken prompt text.

## Rule-Economy & Over-Control Check (judgment-based → REWORK if egregious)

The 20 dimensions and the Behavioral Checklist push toward MORE rules (presence-checks). This is the
counterweight: is the agent over-controlled rather than goal-led? Not a hard fail — a judgment call.
Flag **REWORK** when:

- An **agent-specific** rule has no traceable need (not from `briefing.md`, `research.md`, a
  guardrail, or an observed/live failure) — speculative scar tissue → cut or justify.
- Two rules can contradict on a plausible turn, forcing the model to pick which wins → resolve to one.
- The prompt over-specifies conversational texture the goal already implies (a capable model on
  a current small model derives it) → collapse to goal + latitude.
- Behavioral rules crowd out Flow latitude — no room left for "follow the conversation, not a
  flowchart".

**Scope:** applies to Behavioral Control Layers 2–4 (behavioral leashes, goal/persona, flow —
i.e. objection and tone rules live inside these). **Never** flag Behavioral Control Layer 1
(Guardrail) redundancy — restated hard rules are the safety net. The universal base block is
fleet-validated and exempt. See `../../VOICE-AGENT-PROMPT-ARCHITECTURE.md`.

## Output Format

Write `review-log.md`:

```markdown
# Review Log: <Agent Name>

## Iteration X — <Date>

### Scores
| # | Dimension | Score | Notes |
|---|---|---|---|
| 1 | Naturalness | X | ... |
[all 20 dimensions]

**Overall: X.X/5.0**

### Behavioral Checklist
X/N patterns present (items 38-39 only for engaged-decision-maker agents). Missing: [list]

### Rule-Economy & Over-Control
PASS / REWORK — [speculative rules, contradictions, over-specification, or crowded-out Flow latitude; none if clean]

**Result: PASS / REWORK / ESCALATE**

### Feedback (for dimensions < 4.0 or missing checklist items)
- **Dimension X:** <issue> → <fix instruction>
```

## Review Mindset

Review as if you're a different person than the writer. Be critical. Ask:
- Would a busy Marktleiter stay on this call past 15 seconds?
- Does the objection handling feel empathetic or pushy?
- Are there edge cases the guardrails don't cover?
- Could any instruction be misinterpreted by the LLM?
- Is anything redundant that could be cut without losing behavior?
- Is any rule speculative (no briefing/research/guardrail/observed-failure basis) or in conflict with another — is the agent over-controlled rather than goal-led? (Rule-Economy check.)
- How does this compare to our production benchmark agents?
- Is the prompt within budget (under 10k chars simple / under 18k chars engaged with Answer Bank, ceiling ~18k)? If over, what can be compressed?
