---
name: vac-test
description: Generate test scenarios and evaluate test call transcripts for voice agents. Use after deployment to assess real-world performance. Feeds findings back into prompt iteration. Requires human test callers.
---

# VAC Test

Generate test scenarios, evaluate transcripts, iterate. Output: `test-scenarios.md` + `test-results.md`.

## Requirements (input check)

Before starting, check that these files exist in the agent directory (`../voice-agents/<agent>/`):

| File | Comes from | Missing? |
|---|---|---|
| `briefing.md` | `vac-intake` (step 1) | Run `vac-intake` first |
| `conversation-design.md` | `vac-design` (step 3) | Run `vac-design` first |
| `prompt.md` | `vac-prompt` (step 4) | Run `vac-prompt` first |
| `AGENT.md` (with `agent_id`) | `vac-deploy` (step 6) | Run `vac-deploy` first; no live deployed agent means no test call |
| `deployment-log.md` | `vac-deploy` (step 6) | Run `vac-deploy` first |

If an input is missing, do NOT improvise and do NOT carry on with placeholders: name the missing upstream step and ask the client or the workspace admin whether it should be made up now.

## Process

1. Read all artifacts (briefing through deployment)
2. Generate test scenarios covering all conversation paths
3. **WAIT for human test calls** — provide scenarios to the test callers named by the requester (the client)
4. Receive and evaluate transcripts
5. Score each call, identify patterns
6. Feed findings back into prompt (return to vac-prompt if needed)
7. Max 3 test-iterate cycles, then finalize

## Test Scenario Generation

### Coverage Requirements

Every test suite MUST cover:

| Category | Min Scenarios | Description |
|---|---|---|
| **Happy Path** | 2 | Perfect conversation, prospect cooperates |
| **Objection Path** | 3 | Common objections (kein Interesse, keine Zeit, schon versorgt, zu teuer, Datenschutz) |
| **Gatekeeper** | 1-2 | If outbound: receptionist, assistant, wrong person |
| **Edge Cases** | 2-3 | Angry caller, off-topic questions, the are-you-AI question, silence, unclear speech |
| **Failure Path** | 1-2 | When agent should gracefully exit |
| **Variable Combinations** | 2 | Different Layer 2/3 variable sets |

### Scenario Format

```markdown
## Scenario X: <Name>

**Persona:** <Who the test caller plays>
**Layer 2 Variables:** <firma_name, etc.>
**Layer 3 Variables:** <kandidat_vorname, etc.>
**Objective:** <What this scenario tests>
**Expected Behavior:** <What the agent should do>
**Red Flags:** <What would indicate a problem>

### Script Guidance
<Brief description of how the test caller should behave, key phrases to use>
```

## Transcript Evaluation

### Per-Call Scoring (1-5)

| Dimension | Description |
|---|---|
| **Goal Achievement** | Did the agent reach the primary objective? |
| **Conversation Quality** | Natural flow, appropriate pacing, good listening |
| **Objection Handling** | ARC applied correctly, empathetic, not pushy |
| **Guardrail Compliance** | No violations, appropriate boundaries |
| **Recovery** | How well did the agent handle unexpected inputs |
| **Voice Match** | Does the voice fit the persona and use case? |

### Pattern Analysis

After evaluating all calls, identify:
- **Recurring issues:** Same problem in multiple scenarios
- **Strengths:** What consistently works well
- **Framework effectiveness:** Are the selected frameworks working as designed?
- **Variable handling:** Do dynamic variables integrate naturally?
- **Prompt gaps:** Missing instructions that caused problems

## Iteration Decision

| Overall Score | Action |
|---|---|
| >= 4.0, no dimension < 3.0 | **FINALIZE** — agent is ready |
| 3.0 - 3.9 | **ITERATE** — specific prompt fixes, re-test affected scenarios only |
| < 3.0 | **MAJOR REWORK** — return to vac-design, redesign problem areas |

## Output Format

### test-scenarios.md

```markdown
# Test Scenarios: <Agent Name>

**Agent ID:** <ElevenLabs ID>
**Total Scenarios:** X
**Tester:** <assigned to>

## Scenario 1: <Name>
[scenario format as above]
```

### test-results.md

```markdown
# Test Results: <Agent Name>

**Test Date:** <date>
**Tester:** <Name>
**Iteration:** X of 3

## Call 1: <Scenario Name>

### Transcript
<paste or link>

### Scores
| Dimension | Score | Notes |
|---|---|---|
[6 dimensions]

### Issues Found
- <specific issue with timestamp/quote>

### Fixes Applied
- <what was changed in the prompt>

---

## Summary
- **Overall Score:** X.X/5.0
- **Result:** FINALIZE / ITERATE / MAJOR REWORK
- **Key Patterns:** ...
- **Prompt Changes:** ...
```

## Important

The test phase depends on **human test callers**. Do NOT simulate or fake test results. Wait for real transcripts. If no transcripts arrive, escalate to the requester (the client).
