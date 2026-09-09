---
name: vac-design
description: Design the conversation architecture for a voice agent. Use after research to define conversation phases, transitions, dynamic variables, guardrails, behavioral modules, and no-gos. Produces the conversation blueprint that the prompt writer follows.
---

# VAC Design

Design the conversation architecture. Output: `conversation-design.md`.

> **Prompt architecture foundation:** `../../VOICE-AGENT-PROMPT-ARCHITECTURE.md` — the overarching SSOT
> for rule-vs-goal steering. Pipeline mechanics stay in `PIPELINE.md`.

## Prerequisites (input check)

Before starting, check that these files exist in the agent directory (`../voice-agents/<agent>/`):

| File | Comes from | If missing |
|---|---|---|
| `briefing.md` | `vac-intake` (step 1) | Run `vac-intake` first |
| `research.md` | `vac-research` (step 2) | Run `vac-research` first |

If an input is missing, do NOT improvise and do NOT carry on with placeholders: name the missing upstream step and ask the requester or workspace admin whether it should be run now.

## Process

1. Read `briefing.md` and `research.md`
2. Define conversation phases and transitions
3. Map dynamic variables to the 3-layer architecture
4. Design behavioral modules (greeting protection, closing, adaptive modes)
5. Define guardrails and no-gos
6. Define success/failure/edge-case paths
7. Knowledge Architecture gate: KB needed? (if yes → `vac-knowledge-base` runs next, before vac-prompt)
8. Write `conversation-design.md`

## Behavioral Control Layers (behavior steering)

> **Do not confuse** these with the "3-Layer Architecture (law)" model directly below — that one sorts
> variables by ORIGIN (prompt / variable / dispatcher). THESE layers sort BEHAVIOR by type of control.
> Two different axes. SSOT: `../../VOICE-AGENT-PROMPT-ARCHITECTURE.md`.

Before designing phases and modules, assign every behavior to a control layer. The sorting question is
always: **what happens if the agent gets exactly this decision wrong?**

| Layer | Control | For what | Target section in the prompt |
|---|---|---|---|
| 1 Guardrails | hard rule, "override everything" | irreversible / legal / brand: AI disclosure, no prices, opt-out | `# Guardrails` |
| 2 Behavioral leashes | rule, but soft | conversational texture: one question per turn, reaction policy, Sie-form | `# Conversation Rules`, `# Language Rules` |
| 3 Goal + persona | direction, full latitude | the "why"/"who", not the "how" | `# Identity` |
| 4 Flow | leash, not a script | conversation logic, decided dynamically | `# Conversation Flow` |

**Cost-of-error test per behavior:** catastrophe (legal, brand, irreversible) → layer 1 (hard rule).
Stylistic slip → layer 3/4 (goal + latitude). These layers correspond roughly to the priority order
under "Guardrails Design" (`Guardrails > Conversation Rules > Flow > Objections > Tone`) — both put
guardrails on top. It is NOT a 1:1 mapping, though: goal/persona (layer 3) has no slot there, and flow
is layer 4 here (the softest) but rank 3 in the priority order. The priority order ranks prompt
sections for conflict resolution; the layers classify the type of control.

Consequence for design: steer by the goal by default, and regulate tightly only where the mistake is
expensive. Every narrow rule must trace back to an observed (not hypothetical) failure — see
"Rule Economy" in vac-prompt.

## 3-Layer Architecture (law)

> This is the **variable origin** model (WHERE does a value come from), not the behavior steering from
> "Behavioral Control Layers" above (HOW tightly is a behavior regulated). Different axes.

Every design must map to these three layers:

| Layer | Content | Injected By | Changes |
|---|---|---|---|
| **Layer 1: Static Behavior** | Personality, principles, guardrails, objection handling, behavioral modules | Prompt (hardcoded) | Only on agent update |
| **Layer 2: Customer Context** | Company name, industry, brand voice, products | `{{variables}}` in prompt | Per customer |
| **Layer 3: Dynamic Call Context** | Lead data, call reason, contact person | `{{variables}}` from your dispatcher | Per call |

### Variable Design Rules

Naming: Layer 2 = `{{account_*}}` (the calling account). Layer 3 = `{{lead_*}}`, `{{campaign_*}}`, `{{call_*}}`.

**MANDATORY — the agent name is ALWAYS `{{account_agent_name}}` (since 2026-07-05):** the platform passes the account's agent name on every call as `{{account_agent_name}}` — each account has ONE name for ALL of its voice agents. The persona name is therefore NEVER hardcoded into the prompt again. Use `{{account_agent_name}}` in the prompt as a rendered value, never as an explanation of the key: correct "You are {{account_agent_name}} and call on behalf of …", wrong "Your name is stored in the variable {{account_agent_name}}". Placeholder default = a speakable name that fits the voice (not a marker) — it only takes effect when the dispatch passes nothing. Mind the voice coupling: the voice is fixed per agent, so the account name must match the voice's gender (note it in AGENT.md).

**Dispatch conformity — IMPORTANT:** your dispatcher resolves `lead_*` (10 reserved built-ins: first_name, last_name, phone_number, email, company, title, address, website, industry, notes), `campaign_*` (custom fields) and `account_agent_name` (since 2026-07-05). Name lead master data `{{lead_*}}` accordingly, NOT `{{kandidat_*}}` — otherwise it stays empty in the production dispatch (unknown namespace → empty string). Verify any further `account_*` variables (e.g. `account_name`, `account_info` from the two-namespace pattern) against the outcome mapping before using them.

**MANDATORY for outbound — the dialed number:** every outbound agent MUST carry `{{lead_phone_number}}` in its own prompt block (`# Dialed Number`). Purpose: (1) the placeholder forces the dispatcher to pass the real dialed number (only `{{...}}` vars end up in `dispatch_variables` at schedule time), (2) the agent invents no number when the person called refers to "die Nummer, die Sie angerufen haben" (the number you called). Details in the vac-prompt skill.

**Smart Defaults (CRITICAL):** Every optional variable MUST have a natural German fallback phrase as default — not an empty string. ElevenLabs requires non-empty defaults. The default must work grammatically in the first_message.

Example: `call_ansprechpartner` default = "der Person, die für den Einkauf zuständig ist" so the first_message reads naturally whether or not a name is provided.

**Proper-name variables** (`lead_first_name`, `lead_last_name`) have NO speakable fallback: use a non-empty MARKER default (e.g. "unbekannt") plus a prompt guard ("never speak a placeholder/marker name; if empty or a marker, ask openly who is responsible"). Smart-default PHRASES only work for ROLE variables.

Document in the Variable Map: variable, description, example value, default value, behavior if empty.

## Knowledge Architecture (KB-Gate)

Decide whether this agent needs a RAG knowledge base — BEFORE the prompt is written. A KB holds the long tail of substance an engaged decision maker might ask for.

**KB needed** when BOTH hold: the agent reaches an engaged decision maker with deep/varied questions (inbound-qualify, consultative outbound, own-product sales) AND there is substantial substance beyond the top 3–4 answers (multiple examples, success stories/numbers, detailed how-it-works, company background). **Not needed** for transactional/capture agents, gatekeeper probes, or agents whose substance fits in the prompt.

If KB needed → flag it in `conversation-design.md`; **`vac-knowledge-base` runs next (before vac-prompt)** and owns the prompt-vs-KB split (its 6 boundary tests). If not → note "no KB"; the Answer Bank (if any) carries all substance in the prompt.

## Behavioral Modules (MANDATORY)

Every agent design MUST include specifications for these modules. The prompt writer translates them into prompt text.

### Greeting Protection
- Agent delivers full opening before reacting to caller input.
- How to handle interruption during opener.
- What to ignore (greetings, names, "Ja?", "Hallo?").

### Closing Behavior
- Close Confirmation: what to summarize (one-time).
- Final Closing: appreciation + well-wish (repeatable).
- Post-Close Listen Window: behavior if caller speaks after closing. Reopen limit.
- Follow-up Expectation: WHO will contact them next and WHEN.

### Adaptive Modes
- Mirroring: emotional tone/energy only (domain-vocabulary mirroring is a universal Conversation Rule).
- TIME PRESSURE: compressed behavior when caller has no time.
- RESISTANCE: de-escalation + one ARC attempt + graceful exit.
- DE-ESCALATION: structured response to irritation (acknowledge → responsibility → offer adjustment).

### Conversation Control Rules
- Turn structure: max 2 sentences, ONE action per turn. EXCEPTION: a substantive answer may run ~3 sentences + one re-engaging question.
- Single question per turn: when a turn asks, it asks exactly ONE question — never stack or chain two. Multi-data-point intents (e.g. task + frequency + impact) are gathered across consecutive turns, one question each. (Universal voice-agent principle: sequence questions one at a time.)
- Re-engage after substance: a substantive answer ends with one OPEN question (never a closed "Macht das Sinn?") that re-engages the caller — toward their situation (discovery) or the next step, per the agent's goal.
- Diagnose before you argue: a vague or past-experience objection gets one open diagnostic question first, then tailored substance.
- Reaction Marker Policy: allowed markers, frequency limits.
- Follow-up Budget: 1+1 per topic.
- Non-Repetition: never repeat same intent.
- Answer utilization & signals: incorporate caller info immediately; volunteered facts (prior provider, budget, how they work) are buying signals to explore, not plow past; never reuse a rejected frame word.

### Edge Case Handling
- **Voicemail** (outbound agents): design the *detection*, not a message. The shipped
  outbound overlay sets `voicemail_message: ""` — the agent hangs up instead of speaking,
  because a recorded pitch on a cold call costs more goodwill than it gains. If you do want
  a message left, set `voicemail_message` in the overlay; keep it under 15 seconds, no pitch.
- **Language Barrier**: polite exit, colleague will follow up.
- **Gatekeeper rejection** (outbound): ask for name/email, never pitch.
- **Character Normalization**: define spoken form for "@", ".", "-", "_" in emails/phone numbers.
- **Industry-specific** edge cases (e.g., "Wir arbeiten nicht mit externen Vertriebspartnern" — we don't work with external sales partners).

## Conversation Phase Design

Key principle: **"Follow the conversation, not the flowchart."** Phases are guidelines.

### Per Phase, Define:
- **Intent**: what to achieve (what data to capture, what state to reach).
- **Constraints**: order, follow-up budget, stacking limits — NOT sample questions.
- **Exit conditions**: what triggers moving to next phase.
- **Back-trigger**: when to return to earlier phase.

**CRITICAL — Few-Shot Bias Avoidance (see vac-prompt skill for full guidance):**
Do NOT document phases as lists of sample questions. LLMs reproduce sample lists as templates with minimal variation, producing catalog-style robotic conversations. Instead, document phase intent as: "Find out X (specify what counts as 'found out'), via calibrated questions, in any natural order, phrased in the agent's own words using the caller's vocabulary."

Reusable EXACT phrasings (greetings, closings, transitions, mapping pattern, escalation phrases) are different — those are templates, not examples. Document them clearly and mark them in the prompt with `use this exact phrasing or very close`.

### Typical Structure (adapt per use case)

**Outbound:**
1. Opening + Gatekeeper Navigation
2. Discovery
3. Pitch (max 2 turns)
4. Objection Handling (ARC + diagnose-first, max 2 loops)
5. CTA / Email Capture
6. Closing (with follow-up expectation)
7. Graceful Exit variants

**Inbound:**
1. Greeting / Identification
2. Understanding the inquiry
3. Solution / Qualification
4. Next steps
5. Closing

## Guardrails Design

### Universal (every agent)
- AI disclosure when asked directly
- No unauthorized promises (pricing, availability, samples, discounts)
- DSGVO: no unnecessary data collection
- Consistent register throughout (in German: Sie-Form; adapt to your language)
- Forbidden words: "but", "however", "to be honest"
- Opt-out: immediate, polite exit
- Competitor mention: redirect ("Ich kann nur für [firma] sprechen")
- Technical disclosure: never

### Use-Case Specific
- Design based on industry and customer requirements.
- Explicitly list what the agent may NOT proactively offer (samples, tastings, discounts).
- Define escalation path: specific person name + "meldet sich in den nächsten Tagen".

### Priority Order
```
Guardrails > Conversation Rules > Flow > Objections > Tone
```

## Audio Tag Design

Select 3-5 tags per agent. For each tag define:

| Tag | Mandatory Moments | Optional Moments | Max per Call | Never Use When |
|---|---|---|---|---|

Include governance rules: max 1 per turn, never consecutive turns, never on factual confirmations.

## Output Format

Write `conversation-design.md`:

```markdown
# Conversation Design: <Agent Name>

## Variable Map
### Layer 2 (Customer Context)
| Variable | Description | Example | Default |
|---|---|---|---|

### Layer 3 (Dynamic Call Context)
| Variable | Description | Example | Default | Behavior if Empty |
|---|---|---|---|---|

## Knowledge Architecture
[KB needed? yes/no. If yes: flagged for vac-knowledge-base (it owns the prompt-vs-KB split). If no: note why, Answer Bank carries all substance in the prompt.]

## Behavioral Modules

### Greeting Protection
[spec]

### Closing Behavior
[Close Confirmation, Final Closing, Post-Close Window, Follow-up Expectation]

### Adaptive Modes
[Mirroring, TIME PRESSURE, RESISTANCE, DE-ESCALATION]

### Conversation Control
[Turn structure, Re-engage, Diagnose-first, Reaction Markers, Follow-up Budget, Non-Repetition, Answer utilization & signals]

### Edge Cases
[Voicemail, Language Barrier, Gatekeeper Rejection, Industry-specific]

## Conversation Phases
### Phase 1: <Name>
- **Intent:** ...
- **Key patterns:** ...
- **Exit conditions:** ...

[repeat for each phase]

## Objection Handling (ARC + diagnose-first)
[Use-case-specific objections with response patterns. DEFAULT: on vague or past-experience skepticism ("schon probiert", "war nix"), diagnose before prescribe — one open diagnostic question (what they tried, what disappointed) BEFORE arguing, then address THAT point. A specific question instead gets a direct answer. German trigger labels, English handling.]

## Guardrails & No-Gos
[Universal + use-case specific]

## Audio Tags
[Tag table with governance rules]

## Success Path
[Perfect call, end to end]

## Failure Path
[Graceful exit variants]
```

## Quality Gate

Before proceeding to Prompt:
- [ ] Agent name designed as `{{account_agent_name}}` (rendered-value usage, speakable default) — NOT hardcoded
- [ ] Knowledge Architecture decided (KB needed yes/no; if yes, flagged for vac-knowledge-base)
- [ ] All phases defined with exit conditions
- [ ] Variables mapped with smart defaults (non-empty!)
- [ ] Lead data uses `{{lead_*}}` (dispatch-conform), not `{{kandidat_*}}`
- [ ] Outbound: `{{lead_phone_number}}` mandated in own `# Dialed Number` block (no-invent rule)
- [ ] Behavioral modules complete (Greeting, Closing, Adaptive, Control, Edge Cases)
- [ ] Voicemail handling designed (outbound)
- [ ] Language Barrier handling designed
- [ ] Guardrails complete (universal + specific)
- [ ] Escalation path with named person
- [ ] Audio tags selected with governance rules
- [ ] Follow-up expectation designed (who contacts, when)
- [ ] No unauthorized promises in design
