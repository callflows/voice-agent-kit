---
name: vac-prompt
description: Write the ElevenLabs voice agent prompt and configuration. Use after conversation design to produce the actual prompt (English) and config.json following ElevenLabs best practices. Outbound agents get empty first_message (callee speaks first). Optimized for low latency and natural conversation quality.
---

# VAC Prompt Writer

Write the prompt, first_message, and config.json. Output: `prompt.md` + `config.json` + `example-variables.md`.

> **Prompt architecture foundation:** `../../VOICE-AGENT-PROMPT-ARCHITECTURE.md` — the overarching SSOT
> for rule-vs-goal steering. Pipeline mechanics stay in `PIPELINE.md`.

## Before Writing

1. Read `briefing.md`, `research.md`, `conversation-design.md`
2. Read `references/elevenlabs/prompting-guide.md` for ElevenLabs best practices
3. Read `references/universal-prompt-rules.md` — the mandatory base block for `# Conversation Rules` + `# Language Rules`, built into EVERY agent verbatim
5. If `knowledge-base.md` exists (from vac-knowledge-base): read its **tier-1 spec** — the prompt's Answer Bank carries ONLY tier-1 (high-frequency answers); tier-2 lives in the KB, never duplicate it.

## Core Principle: Latency-Aware Prompt Design

Every token in the prompt costs LLM processing time. Keep the prompt as short as the behavior allows. **Unit = characters of the deployed prompt body** (everything from `# Identity` onward), NOT KB — the KiB-vs-decimal ambiguity decides PASS/fail at the ceiling, so always count characters. The universal base block alone is ~4,700 chars (fixed cost). Soft target **under 10,000 chars** for simple agents; engaged agents with the Answer Bank realistically run **13,000–17,000**. Working ceiling **~18,000 chars** — above it latency degrades noticeably; it is a latency budget (deployable around this size, no documented hard API reject). The ceiling is ~18,000 on current small, fast models, which process longer prompts without the TTFB penalty older models showed. Under-10k is unreachable for engaged agents — do not chase it; the real relief is offloading depth to a knowledge base.

Rules:
- Every sentence must earn its place. No filler, no explanations of WHY something matters.
- Tell the LLM WHAT to do, not WHY it's important.
- One rule per line. No paragraphs of context.
- Formatting is minimal: `#` headings only. No `######`, no `----` dividers, no decorative elements.
- Measure turn length in **sentences** (max 2; a substantive answer may run ~3 + one re-engaging question), not seconds (LLMs can't measure time).

## Core Principle: Rule Economy ("Rules are scar tissue")

Behavior is steered by the goal first, by rules only where a mistake is expensive. Every narrow rule
must trace back to an OBSERVED failure, not a hypothetical one. Start goal-led; add a narrow rule
when live-call feedback, `test-scenarios.md`, or a known fleet failure pattern shows a *repeatable*
failure. (At first-build time before `test-scenarios.md` exists, the evidence is `briefing.md` /
`research.md` and fleet patterns; on iterations it is live-call feedback.)

- Sort each behavior onto a Behavioral Control Layer (see vac-design "Behavioral Control Layers" —
  distinct from the variable "3-Layer (law)" model): hard rule only for irreversible/legal/brand
  (Control Layer 1 Guardrails); soft leash for conversational texture (Control Layer 2); goal +
  latitude for the why/who and flow (Control Layers 3–4).
- **Scope:** this principle governs **agent-specific** additions. The universal base block
  (`references/universal-prompt-rules.md`, copied verbatim) is fleet-validated scar tissue — already
  earned across many builds — and is NOT re-litigated per agent.
- **Stronger models need fewer micro-rules.** On current small models, do not spell out what the
  model already derives from a clear goal — that is latency ballast and rigidity, and the first
  thing to cut.
- **Guardrail redundancy is a safety net, not filler** — a hard rule restated as an override stays.
  Rule economy applies to Behavioral Control Layers 2–4, never to Control Layer 1 (Guardrails).

### Rule of thumb for non-technical readers

The core decision tree when you are weighing whether something needs a hard rule:

If the agent gets this one thing wrong, does it cause:
- (a) something legal, irreversible, or brand-damaging → hard rule (guardrail).
- (b) an embarrassing but harmless slip → NO rule, the goal handles it.

New rules only after observed misbehavior in real calls, never on suspicion.

Guardrail examples (a): naming prices or discounts; committing to firm delivery dates; claiming not to be an AI assistant.
NOT-a-guardrail examples (b): a greeting that is too formal or too casual; one clumsily phrased question; the occasional wrong filler word. The goal adjusts that, not a rule of its own.

## CRITICAL: Intent Specs over Sample Utterances (Few-Shot Bias Avoidance)

LLMs treat example phrases as in-context templates and reproduce them with minimal variation — even with "These are illustrative" markers. Voice agents amplify this because TTS speaks the examples literally. The result is robotic, catalog-style conversations where the agent walks through example questions in the exact order they appear in the prompt.

### Hard rules

- **NEVER include lists of sample questions for Discovery, Implication, Fit Check, or any data-gathering phase.** Define INTENT (what to find out) + CONSTRAINTS (style, follow-up budget, order), not example utterances.
- **NEVER include sample dialogues** that show "the agent says X, the caller says Y, the agent says Z".
- **NEVER include multiple example phrasings** "for variation" — that produces the opposite: the model picks one and reuses it.
- **ALWAYS instruct the model to phrase in its own words**: "phrase every question in your own words. Never recite identical phrasings — vary across and within calls."
- **ALWAYS instruct the model to use the caller's vocabulary**: when the caller has said "Bewerbungen sichten", the agent should ask about THAT specific phrase, not generic "Tagesgeschaeft".

### What's still ALLOWED (and recommended)

The following are NOT few-shot examples — they are explicit reusable artifacts. Mark them clearly with `use this exact phrasing or very close`:

| Type | Example use |
|---|---|
| **Mandatory Templates** | First message, Final Closing, Bridge to Booking transition, Mapping pattern, Time-saving statement pattern |
| **Anti-Patterns** | Forbidden words ("but", "however"), evaluative markers ("great", "perfect") — these reduce mimicry, not increase it |
| **Linguistic Patterns** | Address-form rules ("Sie" for person vs "ihr" for company) with short examples — these are grammatical patterns, not dialog |
| **Escalation Phrases** | Short fixed exit lines (e.g. "Das nimmt Benjamin direkt mit auf.") — repeated use is fine |
| **ARC Intent** | For each anticipated objection, state Acknowledge + Reframe + Continue as INTENT (no wording). Never list the full ARC phrase. |

### Mimicry-Test before deploy

For every section in the prompt, ask: "Would a junior LLM treat this as a template to recite?"
- If the section contains 2+ similar-shape phrasings → suspect Few-Shot Bias → refactor to intent.
- If the section contains a phrase that MUST be said exactly that way (greeting, closing, transition) → mark as `use this exact phrasing` and keep.

### Conversation-Rules enforcement (base block)

Every prompt MUST contain in Conversation Rules (all part of the `universal-prompt-rules.md` base block, copied verbatim):
- "Variation: phrase every question in your own words. Never recite identical phrasings — vary across and within calls."
- "Answer utilization & signals: use every fact the caller shares; a volunteered prior provider/budget/how-they-work is a buying signal to explore, not plow past. Never re-ask captured info; never reuse a frame word they rejected."
- "Re-engage after substance" (open question, never closed "Macht das Sinn?"), "Diagnose before you argue" (one open diagnostic question on vague/past-experience skepticism), and "Mirror the caller's domain vocabulary" — see the base block.

## Prompt Architecture

Prompt in **English** (better LLM processing). The agent speaks whatever
`conversation_config.agent.language` is set to — English by default.

### Mandatory Sections (in this order)

```
# TURN 1 — ABSOLUTE RULE (outbound only — MANDATORY, must be the FIRST block)
# Identity
# Conversation Rules
# Language Rules
# Greeting Protection
# Closing Behavior
# Adaptive Modes
# Audio Tags
# Context Variables
# Dialed Number (outbound only — MANDATORY)
# Conversation Flow (with subsections per phase)
# Guardrails
```

### Section Content Guide

**# TURN 1 — ABSOLUTE RULE** (outbound only — FIRST block, before `# Identity`)
**SSOT: `references/universal-prompt-rules.md`** (the `# TURN 1 — ABSOLUTE RULE` base block). Outbound agents only (`first_message` = `""`); for inbound the block is dropped with no replacement. Copy the scaffold verbatim, fill the per-build slots: the `<OPENER>` **identical** to `# Opening` (deliberate redundancy for turn-1 hardening) and 4 WRONG/RIGHT few-shots with real or industry-typical first utterances. Purpose: on turn 1 the model ALWAYS delivers the full opener, never a reaction to the (often STT-garbled) first user input. Once it is in place, `# Greeting Protection`, `# Opening`, the reaction policy, and the guardrails MUST all reference this block consistently.

**# Identity**
- Who the agent is, role, company, conversion goal. 3-5 sentences max.
- **Agent name = `{{account_agent_name}}`, NEVER hardcoded (convention):** the platform passes the account agent name on every call. Write it as a rendered value: "You are {{account_agent_name}}, the digital assistant of …" — never as an explanation of the key ("Your name is stored in {{account_agent_name}}"). Applies everywhere the agent names itself: Identity, Opening/`# Opening`, first_message (inbound), voicemail message. Placeholder default: a speakable name that fits the voice.
- Internal mindset (one sentence).
- What the agent is NOT (salesperson, decision maker, etc.).
- Brand personality in one line.
- "All spoken output MUST be in German using formal 'Sie'."

**# Conversation Rules**
**SSOT: `references/universal-prompt-rules.md`.** Copy the `# Conversation Rules` base block from that file verbatim into every agent — it covers turn mechanics, single-question rule, reaction policy, follow-up budget, answer utilization, non-repetition, variation, and Sie-consistency. Do NOT re-list those rules here or in the prompt; the reference file is the single source. Below the base block, add only **agent-specific** conversation rules (e.g. a DU-mirror exception, an industry-specific addressing convention).

**# Language Rules**
**SSOT: `references/universal-prompt-rules.md`** (`# Language Rules` base block — natural phrasing, forbidden words, no system-logic reveal, character normalization). Copy verbatim, then add only **agent-specific** language rules (e.g. forbidden framings unique to this brand, extra normalization for domain terms).

**# Greeting Protection** (CRITICAL — mark with "This step is important")
- Agent MUST deliver full opening before reacting to caller content.
- Ignore "Ja?", "Hallo?", names, short greetings during first utterance.
- If interrupted: stop, acknowledge briefly, complete in shortened form. Never restart.
- **Outbound:** this block is the soft restatement of the hard `# TURN 1 — ABSOLUTE RULE` above — it points to it ("see also the TURN 1 — ABSOLUTE RULE, which governs") and must not contradict it. The interrupt case explicitly means "interrupts your opener MID-DELIVERY", not the first utterance of the person called (that is always to be ignored).

**# Closing Behavior**
Two distinct elements:
- A) CLOSE CONFIRMATION (one-time): summary of agreed next step + follow-up expectation (WHO will contact them, WHEN).
- B) FINAL CLOSING (repeatable): short appreciation + well-wish. No summary, no question.
- Post-Close Listen Window: silent 3s, if caller speaks → ONE short answer → repeat ONLY final closing. Max 1 reopen. Never resume pitch.

**# Adaptive Modes**
- Mirroring: mirror emotional tone and energy, never slang/negativity/aggression. (Domain-vocabulary mirroring — adopt the caller's own business terms — is a universal Conversation Rule, see `references/universal-prompt-rules.md`.)
- TIME PRESSURE: acknowledge briefly, compress to 1-sentence pitch + CTA, close cleanly, never re-open.
- RESISTANCE: de-escalate in one sentence, one ARC attempt, if continues → graceful exit.
- DE-ESCALATION: (1) acknowledge emotion, (2) light responsibility without defensiveness, (3) offer to shorten/pause/stop. Never defend, argue, or ignore. If they re-engage, resume without mentioning conflict.

**# Audio Tags**
- Usage rules: max 1 per turn, never consecutive, never on DATA (prices, dates, numbers, contact data) or factual confirmations. Positioning/USP statements are not data and MAY take [firmly].
- Mandatory moments: opening, final closing, caller hesitation/frustration.
- Optional moments: product USP, emotional acknowledgment, de-escalation.
- Tag mapping table: which tag for which situation.
- Format: `[tag_name]` at sentence start.
- "When in doubt: prioritize structure over creativity, clarity over charm, calm authority over friendliness."

**# Context Variables**
- Table with: variable name, behavior if empty.
- "Only reference variables with real values. Never mention variable names in output."
- **Proper-name variables** (`lead_first_name`, `lead_last_name`) have no speakable fallback: give a non-empty MARKER default (e.g. "unbekannt") + a guard "never speak a placeholder/marker name; if empty or a marker, ask openly who is responsible." Smart-default phrases only work for ROLE variables (e.g. `call_ansprechpartner`).
- For warm leads: note how `call_kontext` changes the opening.

**# Dialed Number** (outbound agents — MANDATORY, own block)
- Outbound agents reach the lead on a known number. Expose it as `{{lead_phone_number}}` (E.164) so the agent never invents one.
- The name MUST be exactly `lead_phone_number` — a reserved built-in the your dispatcher resolves per call. Other namespaces (`kandidat_*`, `call_*`) do NOT resolve on the production dispatch path.
- Mechanic: only `{{...}}` placeholders present in the prompt enter `dispatch_variables` at schedule time, so the placeholder itself is what forces the dispatcher to pass the real number. Without it the agent has no access to the dialed number and WILL hallucinate one when asked (verified failure mode, June 2026).
- Rules the block must state:
  - If the caller offers "the number you called" / "the known one" for follow-up → use `{{lead_phone_number}}`. Read it back digit by digit only on explicit request.
  - NEVER invent or guess a phone number. If none is on hand and the caller names none, ask or leave it open — never read back a guessed number.
  - Capture a DIFFERENT direct line only when the caller explicitly states it.
- After adding/removing the placeholder, the campaign must be re-scheduled/re-validated so `dispatch_variables` picks it up.

**# Conversation Flow**
- "Phases are guidelines. Follow the conversation, not a flowchart."
- Subsections for each phase with: intent, key dialogue patterns, exit conditions.
- Include: Gatekeeper navigation, Discovery, Pitch, Objection Handling (ARC, use-case-specific), CTA/Email Capture, Closing, Graceful Exit.
- Voicemail handling (outbound agents MUST have this) — recognize the answering machine and
  end the call. Do not write a message to be spoken: the shipped overlay hangs up.
- Language Barrier handling.
- "This step is important" on critical rules (gatekeeper-never-pitch, pricing-never-name, opt-out-immediate).

**# Answer Bank (CONDITIONAL — agents that reach an engaged decision maker)**

Not every agent needs this. Add it when the agent reaches someone who asks real questions (inbound-qualify, consultative outbound, any agent selling its OWN product). Skip it for pure transactional capture (a booking, a single data point). **Position:** after `# Language Rules`, before `# Conversation Flow`; conditional, so it is not in the mandatory-sections order above.

- **Boundary by use case (decides answer-vs-redirect):**
  - *Sells its own product* (e.g. an agency selling its own service): ANSWER who/what the company is, how it works at a high level, the benefit, ONE concrete example, data protection, "are you AI". DEFER only price + deep technical configuration to website/appointment.
  - *Must not advise* (assistant fronting a named human expert, e.g. Goltz): narrower — answer context/trust only, redirect domain/advice questions to the named human. The redirect-vs-answer choice is use-case-dependent, NOT a contradiction between builds.
- **Not a pitch:** answer the SPECIFIC question concisely; never an unsolicited use-case list or mini-pitch (that collides with the no-pitch / no-enumeration doctrine).
- **Substance source:** for KB builds (see vac-knowledge-base), the Answer Bank carries ONLY tier-1 (high-frequency answers) + a "draw on the knowledge base, in your own words" instruction; tier-2 substance lives in the KB, never duplicated here. For non-KB builds, all approved substance sits in the prompt.
- **Style:** intent-specs, never canned sentences. German trigger labels + English handling (see `references/universal-prompt-rules.md`). 1-3 sentences, then RE-ENGAGE with one open question.
- **Pair with "Diagnose before you argue":** on vague or past-experience skepticism, ask one open diagnostic question BEFORE giving substance.

**# Guardrails**
- "These rules override everything else. No exceptions."
- NEVER/ALWAYS format, one rule per line.
- Must include: pricing, discounts, competitors, availability/delivery, samples/tastings, opt-out, forbidden words, Sie-form, AI disclosure, outbound respect, technical disclosure, gatekeeper, binding commitments.
- Escalation path with specific person name.

### What NOT to Include

- Explanations of WHY a rule exists (the LLM doesn't need motivation)
- Redundant formulations of the same rule
- Decorative formatting (######, ------, ****)
- `agent_rolle` in spoken output (internal only)
- Data collection instructions (tracking is external)
- Promises the business hasn't authorized (samples, tastings, discounts)
- Hardcoded values that should be variables

## first_message

### Outbound Agents: first_message MUST be empty (`""`)

**Why:** When someone is called, they pick up and say "Hallo?" or their name FIRST. If `first_message` is set, ElevenLabs fires it as TTS immediately — before the callee speaks. This feels unnatural and aggressive.

**How it works instead:**
1. `first_message` = `""` (empty string) in config.json
2. The callee picks up and says something ("Hallo?", "Müller?", "Ja bitte?")
3. The LLM receives this as the first user turn
4. The LLM responds with the opening greeting — ALWAYS the full opener, never a reaction to what the callee said (enforced by `# TURN 1 — ABSOLUTE RULE`; the opener text lives under `# Opening`)

**Turn-1 hardening is mandatory (not optional):** every outbound agent gets the `# TURN 1 — ABSOLUTE RULE` block as the very first prompt block (SSOT: `references/universal-prompt-rules.md`). Without it, weaker LLMs (verified on gpt-5.4-mini) react to the first — often STT-garbled — user input instead of opening, skipping AI disclosure and opener. The opener therefore appears deliberately in TWO places (turn-1 block + `# Opening`), word for word identical.

**Prompt must contain an Opening section** that tells the LLM what to say. For outbound it points to the turn-1 block and must not contradict it:
```
# Opening
TURN 1 IS ALWAYS THIS OPENER (see the top rule) — you do NOT classify or react to the first utterance.
Deliver your greeting: identity + company + reason for calling + verify right person.
Use [warmly] audio tag. Max 2-3 sentences.
Silence fallback: if the callee stays silent for >3s AFTER you delivered the opener, re-anchor once with "Guten Tag, hier ist {{account_agent_name}} von [Firma]." This is a follow-up to an unanswered opener, never a substitute for turn 1.
```
The agent name in the opening (and in every other spoken self-reference) is ALWAYS `{{account_agent_name}}`, never a hardcoded name (see `# Identity`).

**Variables in the opening** are handled via prompt instructions referencing `{{variables}}` — the LLM resolves them at runtime, same as any other turn.

### Inbound Agents: first_message can be set

For inbound agents (caller dials in), a first_message is appropriate because the agent should greet immediately.

Rules:
- Uses `{{variables}}` — including optional ones with smart defaults.
- **Smart Default Pattern**: For optional variables like `call_ansprechpartner`, set the DEFAULT to a natural German phrase (e.g. "der Person, die für den Einkauf zuständig ist"). When a real name is provided at runtime, it overrides. This way ONE first_message handles all cases. No IF/ELSE needed.
- Max 2-3 sentences.
- Audio tag at start if using expressive mode (e.g. `[warmly]`).
- Clear reason for calling + verification of right person.
- **ElevenLabs requires non-empty defaults** for all dynamic_variable_placeholders.

## config.json

```json
{
  "name": "<agent-name>",
  "conversation_config": {
    "agent": {
      "prompt": { "prompt": "SEE prompt.md" },
      "first_message": "",
      "language": "de",
      "dynamic_variables": {
        "dynamic_variable_placeholders": {
          "<var>": "<non-empty default value>"
        }
      }
    },
    "tts": {
      "voice_id": "PLACEHOLDER_SELECT_IN_DEPLOY",
      "model_id": "eleven_v3_conversational",
      "expressive_mode": true,
      "suggested_audio_tags": [
        {"tag": "<TagName>", "description": "<usage rule, max 200 chars>"}
      ]
    },
    "turn": {
      "turn_timeout": 10,
      "silence_end_call_timeout": 30,
      "turn_eagerness": "eager",
      "soft_timeout_config": {
        "message": "<natural filler in German, e.g. 'Moment...' or 'Mhm...'>",
        "timeout_seconds": 3,
        "use_llm_generated_message": true
      }
    }
  }
}
```

### Config Rules
- API field for turn settings is `turn`, NOT `conversation`.
- `turn_eagerness`: set by the use-case overlay at deploy time and it wins over anything you
  put here — outbound `normal` (cold-call recipients get talked over otherwise), inbound
  `eager`. Only override deliberately, e.g. `patient` for data collection.
- `soft_timeout_config.timeout_seconds`: 2-3s recommended (max 8). Prevents awkward silence.
- All `dynamic_variable_placeholders` MUST have non-empty default values (ElevenLabs requirement).
- For ROLE/optional variables: a natural fallback phrase (e.g. "der Person, die für den Einkauf zuständig ist"). For PROPER-NAME variables (first/last name): a non-empty marker (e.g. "unbekannt") + a prompt guard against speaking it — there is no speakable name fallback.

### Audio Tags (MANDATORY)

1. Read Audio-Tag table from conversation-design.md.
2. For each tag: `tag` = exact name, `description` = usage rule (max 200 chars).
3. Read `references/elevenlabs/audio-tags.md` for valid tag names.
4. Include governance rules (mandatory/optional moments) in the prompt itself, not just config.

## Example Variables (MANDATORY)

Create `example-variables.md` with plausible test values.

Rules:
- Min. **3 scenarios**: (1) default/cold, (2) with known contact, (3) warm lead or edge case.
- Scenario 1 = ElevenLabs Dashboard defaults.
- All variables covered. Edge case scenario tests empty optional variables.
- Smart defaults documented in the `Hinweise` section.
- Update on every prompt change.

### Format (the artifact itself is written in German)

```markdown
# Beispiel-Variablen: <Agent Name>

## Szenario 1: <Default — wird im Dashboard hinterlegt>
### Layer 2 (Kundenkontext)
| Variable | Wert |
|---|---|
| `var` | value |

### Layer 3 (Call-Kontext)
| Variable | Wert |
|---|---|
| `var` | value |

## Szenario 2: <Other constellation>
[...]

## Szenario 3: <Edge case / warm lead>
[...]

## Hinweise
- Smart default explanations
- Variable dependencies
```

## Output

Write to the agent's directory:
- `prompt.md` — Full prompt (English) with first_message (German) at top
- `config.json` — ElevenLabs configuration with all required fields
- `example-variables.md` — Min. 3 test scenarios

Format:
```markdown
# Prompt: <Agent Name>

## First Message (German)
> <first_message text>

**Note:** <smart default explanation if applicable>

## Prompt (English)
<full prompt — compact, no decorative formatting>
```

## Quality Gate

Before proceeding to Review:
- [ ] Prompt in English, German only in examples/first_message
- [ ] Agent name via `{{account_agent_name}}` (rendered value) in Identity + Opening/first_message — no hardcoded persona name, placeholder with a speakable default
- [ ] All mandatory sections present in correct order
- [ ] Deployed prompt body (chars from `# Identity`): <10,000 simple / 13,000–17,000 engaged (Answer Bank), ceiling ~18,000. Measure in characters, not KB.
- [ ] No decorative formatting (no ######, no ------, no ****)
- [ ] Turn length in sentences (max 2; substantive answers ~3 + question), not seconds
- [ ] Greeting Protection present with "This step is important"
- [ ] Post-Close Listen Window with reopen limit
- [ ] Adaptive Modes: TIME PRESSURE + RESISTANCE + DE-ESCALATION
- [ ] Reaction Marker Policy with frequency limits
- [ ] Follow-up Budget (1+1 rule)
- [ ] Character Normalization for email/phone
- [ ] Voicemail handling (outbound agents)
- [ ] Language Barrier handling
- [ ] Few-Shot Bias check: no sample-question lists in Discovery/Implication/Fit-Check (intent specs only)
- [ ] Variation rule present in Conversation Rules
- [ ] Reusable templates explicitly marked with `use this exact phrasing or very close`
- [ ] Outbound agents: first_message is empty (`""`), opening greeting in prompt under `# Opening`
- [ ] Outbound agents: `# TURN 1 — ABSOLUTE RULE` block present as the FIRST block (before `# Identity`), opener verbatim-identical to `# Opening`, 4 WRONG/RIGHT few-shots; Greeting Protection + Opening + Reaction-Policy + Guardrails reference it without contradiction; silence fallback framed as follow-up, not substitute
- [ ] Outbound agents: `# Dialed Number` block present with `{{lead_phone_number}}` + no-invented-number rule
- [ ] Inbound agents: first_message uses smart default pattern for optional variables
- [ ] All dynamic_variable_placeholders have non-empty defaults
- [ ] config.json uses `turn` key (not `conversation`)
- [ ] soft_timeout_config present (2-3s)
- [ ] turn_eagerness set appropriately
- [ ] Audio Tag governance rules in prompt (mandatory/optional moments)
- [ ] Guardrails include: pricing, samples, competitors, opt-out, AI disclosure
- [ ] Follow-up expectation in closing (WHO contacts, WHEN)
- [ ] No promises business hasn't authorized
- [ ] example-variables.md with min. 3 scenarios
