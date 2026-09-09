# Voice-agent prompt architecture — base document

> **Purpose:** the binding foundation for how voice-agent prompts are built in this repo.
> Applies to the `vac-skills` (conversation design, prompt generation, review) and to every agent
> under `voice-agents/`. Where a skill instruction and this document conflict **on prompt-architecture
> questions** (rule vs. goal steering, layer assignment, guardrail hardness), this document wins
> until the skill has been brought in line. For **pipeline mechanics** (steps, output files, order)
> `PIPELINE.md` remains the SSOT. The two documents govern different axes and do not contradict
> each other.
>
> **Status:** Base v1 · 2026-07-07 · reference implementation: `voice-agents/general-pdl-job ads/prompt.md`

---

## Core thesis

The question "many individual rules vs. few rules + goal definition" is **the wrong question**. It
is not an either-or. Production voice agents are **layered hybrids**. The actual design decision is
not "how many rules" but **which decision belongs on which layer**.

The sorting variable is always the same:

> **What happens if the agent gets this particular decision wrong?**
> Catastrophe (legal, brand, irreversible) → hard rule.
> Stylistic slip → goal definition + latitude.

Both platform practice (Vapi Prompting Guide) and research (Conversation Routines, arXiv
2501.11613) converge on the same layered hybrid. Pure approaches fail in both directions (see
below).

---

## The 4-layer model

Every agent behavior is assigned to exactly one layer:

| Layer | Steering | For what | Prompt section (reference) |
|---|---|---|---|
| **1. Guardrails** | Hard rules, deterministic, "override everything" | Irreversible / legal / brand: AI disclosure, no prices, immediate opt-out, no invented facts, no live transfers | `# Guardrails` |
| **2. Behavioral guardrails** | Rules, but soft | Conversation texture: one question per turn, reaction policy, formal-Sie consistency, follow-up budget | `# Conversation Rules`, `# Language Rules` |
| **3. Goal definition + persona** | Direction, full latitude | The "why" and "who", not the "how" | `# Identity` (incl. goal statement) |
| **4. Flow** | Guardrails, not a script | Conversation logic, decided dynamically | `# Conversation Flow` — *"Phases are guidelines. Follow the conversation, not a flowchart."* |

The one line from layer 4 — **"Follow the conversation, not a flowchart"** — is the goal-oriented
latitude, embedded in a rule-based document. That is the hybrid in a single sentence.

---

## Why the pure approaches fail

### Pure rules (maximum control)
- **Combinatorial explosion:** one rule for every conversational possibility → an unmaintainable prompt.
- **The underrated killer — rule conflicts:** beyond a certain volume, rules contradict each other.
  Then the model decides for itself which one wins after all. What you have is not control but the
  *illusion* of control plus a bloated prompt.
- **Rigid scripts sound like an IVR menu.** On the phone that is instantly fatal.

### Pure goal (maximum dynamics)
- **Unobservability:** failure modes differ per call → not testable, not debuggable.
- **Compliance risk:** in outbound cold outreach in Germany, "unwanted conversation handling" is not
  a style problem but a legal risk (EU AI Act disclosure obligation, GDPR, no quoting of prices).
  An agent that forgets the AI disclosure in 3 % of calls is not suboptimal, it is grounds for a
  cease-and-desist.

**Note:** "the model mostly sticks to it" is not an acceptable error rate for compliance. That is why
layer 1 always stays hard — no matter how good the model gets.

---

## Model quality shifts the optimum

The rule-heavy style is partly **legacy from weak models**. In 2023 every nuance had to be spelled
out. Current models (Claude Haiku 4.5, Opus 4.8, GPT-5.4 and -mini) follow instructions well enough that **few,
high-altitude rules + a clear goal** now achieve more than 40 micro-rules did back then.

**Consequence for new agents:** on a strong model, slide towards goal latitude — **except on the
guardrails**. Micro-rules that a strong model derives from the goal anyway are ballast.

---

## The two rules of thumb

**1. The layer test (for every single rule):**
> "If the agent does the opposite of this instruction: catastrophe or just a slip?"
> Catastrophe → guardrail (layer 1). Slip → goal + latitude (layer 3/4).

**2. Rules are scar tissue:**
> Every rule must be traceable to an **observed** failure in real calls, not a hypothetical one.
> Start goal-heavy. Only add a rule once the eval set shows a *repeatable* failure. Otherwise the
> prompt grows against phantoms.
>
> **Exception, fleet-validated base blocks:** rules that have been observed across many builds and
> rolled out as a shared verbatim block (e.g. the skills' universal base block) count as
> observation-backed. They are exempt from this check AND from layer-2 compression.
> Rule economy applies only to the **agent-specific** additions on top.

---

## Empiricism beats opinion

Exactly where the line between rule and goal falls is **not a matter of opinion but an eval question.**

- Validate prompt changes **against a representative test set**, never against individual calls.
  Probabilistic regressions only become visible across many iterations.
- Without a golden set of test calls, cutting means **blindly trading control for brevity**.
- Compression means: remove layer-2/3/4 redundancy and meta commentary. **Layer-1 redundancy
  (guardrails as a hard override) is a safety net, not fat** — do not touch it.

---

## Checklist for prompt generation & conversation design

A generated prompt / a conversation design satisfies this base document if:

- [ ] **Layers are separated** — guardrails, behavioral guardrails, goal/persona and flow stand as
      clearly distinguishable sections, not mixed together.
- [ ] **Guardrails are explicit and hard** — compliance/irreversible/brand items stand as an
      "override everything" block. AI disclosure, no prices, opt-out, no invented facts are
      included wherever applicable.
- [ ] **Flow is a guardrail, not a script** — an explicit sentence gives the model latitude
      ("Follow the conversation, not a flowchart" or similar).
- [ ] **Goal comes before tactics** — the "why" of the call is stated before detailed rules follow.
- [ ] **No micro-rule without failure evidence** — every narrow rule addresses an observed, not a
      hypothetical problem.
- [ ] **Model-appropriate** — on a strong model, do not spell out what the model derives from the goal.
- [ ] **An eval anchor exists** — there are test scenarios / a golden set for changes to run against
      (on iterations; on a first build, briefing/research serve as failure evidence and the test set
      follows).
- [ ] **Compression respects layer 1** — guardrail redundancy is preserved when cutting.

---

## Sources

- [Vapi Voice AI Prompting Guide](https://docs.vapi.ai/prompting-guide) — 6-section structure,
  guardrails as absolute overrides, pragmatic hybrid (prompt for guidance, server-side for
  safety-critical items).
- [Conversation Routines: A Prompt Engineering Framework for Task-Oriented Dialog Systems (arXiv 2501.11613)](https://arxiv.org/html/2501.11613v3)
  — moderate structure (natural-language rules instead of free-form) balances reliability and
  naturalness; LLM non-determinism remains a residual risk.
- [How to Prompt Your AI Voice Agent (Aloware)](https://aloware.com/blog/how-to-prompt-your-ai-voice-agent)
  — four pillars persona/context/rules/knowledge; validate changes against a test set.
- [Prompt Engineering for AI Agents (PromptHub)](https://www.prompthub.us/blog/prompt-engineering-for-ai-agents)
- [Architecting Prompts for Agentic Systems (JB, Medium)](https://medium.com/@jbbooth/architecting-prompts-for-agentic-systems-aligning-ai-behavior-with-human-expectations-25b689b3b8f6)
  — prompt architecture makes probabilistic output structured and aligned with expectations.
