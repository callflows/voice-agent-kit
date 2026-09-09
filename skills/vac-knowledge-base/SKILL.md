---
name: vac-knowledge-base
description: Decide what goes in the prompt vs. a RAG knowledge base, then author the KB document for an engaged-decision-maker voice agent. Use after vac-design (when it flags "KB required") and BEFORE vac-prompt, so the prompt writer knows the prompt-vs-KB split. Produces knowledge-base.md (tier-2 substance, RAG-style) + a tier-1 spec for the prompt. CONDITIONAL step — not every agent needs a KB.
---

# VAC Knowledge Base

Draw the prompt-vs-KB boundary, then author the KB. Output: `knowledge-base.md` + a tier-1 spec handed to `vac-prompt`.

**Position in the pipeline:** runs after `vac-design` (which flags whether a KB is needed) and **before** `vac-prompt`. This way the prompt writer puts only tier-1 substance into the Answer Bank and adds a "knowledge base available" hook; tier-2 is never duplicated in the prompt.

**This skill does NOT deploy.** Upload + RAG-index + attach belong to `vac-deploy` (scripts in `vac-elevenlabs-api`).

## When a KB is warranted (the gate)

A KB is for the **long tail of substance** an engaged decision maker might ask for. Build one only when BOTH hold:

- The agent reaches an **engaged decision maker** with deep/varied questions (inbound-qualify, consultative outbound, any agent selling its OWN product). Same condition as the Answer Bank.
- There is **substantial substance beyond tier-1**: several concrete examples, success stories/numbers, detailed how-it-works, company background, edge-case objections, secondary use-cases.

**Skip the KB** for pure transactional/capture agents, gatekeeper-only probes, or agents whose whole substance fits comfortably in the prompt. Answer Bank without a KB is fine — tier-1 alone can be enough. The KB is the *subset* where the long tail justifies RAG.

## Source material

Company-info KBs source their tier-2 detail from **`vac-company-research` (Step 4b: KB-Detail)** — it gathers the prospect-level detail (detailed how-it-works, examples, metrics, company background, FAQ) and already flags the guardrail-taboo content to exclude. On the auto path it ran at Step 0; on the human-intake path, run its Step 4b pass (or gather the detail yourself) before authoring. The few core company facts + the call purpose are its tier-1 and reach the prompt via briefing/design. The KB is only as good as this source — this skill structures and voices the substance, it does not invent facts.

## Quick decision for non-technical readers

Four yes/no questions. They lead to the same result as the 6 tests below:

- Do the facts change often (prices, availability, locations, numbers)? Yes → KB (maintainable there, without touching the prompt).
- Does the agent need the info in nearly every conversation? Yes → prompt. Only when individual prospects dig deeper? → KB.
- Would it be bad if the agent did NOT have the info at hand? Yes, it has to land every time → prompt. No, "nice if asked" → KB.
- Is it sensitive material (prices, firm delivery dates, cost comparisons, customer names)? Yes → belongs NEITHER in the KB nor as a fact in the prompt; it becomes a hard rule instead (see test 5).

When unsure, the detailed table below applies; if in doubt, ask the client.

## The boundary: 6 tests (run per info block)

| # | Test | → Prompt | → KB |
|---|---|---|---|
| 1 | **Frequency** | needed by >~50% of engaged calls | long tail |
| 2 | **Criticality** | must always be available / never missed / verbatim | nice-to-have-when-asked |
| 3 | **Size** | fits the budget | would push the prompt body over ~13,000–15,000 chars → offload |
| 4 | **Volatility** | stable | facts/numbers change often → KB (update without re-writing the prompt) |
| 5 | **Guardrail taboo** | price → a prompt RULE ("never name a figure") | price / hard delivery-time promises / cost comparisons / named reference customers are EXCLUDED from the KB (RAG could surface them) |
| 6 | **Retrieval reliability** | correct behavior depends on it being present EVERY turn (RAG can miss) | safe to occasionally not retrieve |

Rule of thumb: **the top 3–4 answers + everything behavior-critical → prompt. Everything else substantive → KB.** Test 6 is the strongest guard against over-offloading: never put in the KB anything the agent MUST be able to say reliably.

## tier-1 spec (handed to vac-prompt)

After the split, write a short tier-1 list for the prompt writer: the high-frequency answers that stay in the prompt's Answer Bank (as intent-specs, German trigger labels, English handling — see `vac-prompt/references/universal-prompt-rules.md`). Typically: the value framing, the "who are you" one-liner, "how does it work" at a high level, ONE flagship example, "are you AI", the data-protection one-liner. Everything else → KB. Note in the spec that a KB is attached so the prompt's Answer Bank carries a "draw on the knowledge base, in your own words" instruction.

## Authoring rules (KB content)

The KB is retrieved and **spoken**. Write it to be paraphrased, not recited.

- **Spoken, paraphrasable German prose.** Short paragraphs (chunk-friendly), no bullet-list-as-script, no canned sales sentences — RAG injects chunks near-verbatim, so a scripted KB parrots the same way few-shot examples do.
- **Question-anchored section headers** (e.g. "### Wie der Assistent eingerichtet wird") so RAG semantic match maps a caller's question to the right chunk.
- **Meta / payload split** (see structure). Only the payload is uploaded. **NEVER write the literal upload-marker string `## KB Content (Upload)` inside the meta block prose** — the uploader cuts at the first occurrence of that string, so an in-prose mention makes it cut inside the meta and leak the rest into the KB (verified bug 2026-06-22). Refer to it as "the content section below", never verbatim. After upload, `GET /knowledge-base/{id}/content` and confirm 0 meta markers.
- **Guardrail-taboo EXCLUSIONS — keep OUT of the payload:** prices, hard delivery-time promises, cost comparisons, named reference customers. RAG would surface them and break a guardrail. Soften timelines ("in wenigen Wochen", not "in 14 Tagen").
- **Fact/number review flags** in the meta block: every metric a human must confirm before deploy goes on a `[ ]` checklist.
- **Payload > 500 bytes** (RAG indexing minimum) and well under the workspace limit (~300k chars non-enterprise).

## knowledge-base.md structure

```markdown
# Knowledge Base: <Agent Name>

## Meta — do not upload
**Upload boundary:** only the "## KB Content (Upload)" section goes into the ElevenLabs KB.
**Deliberately NOT in the KB** (guardrail taboo): prices, firm dates, cost comparisons, customer names.
**Review flags (numbers to sign off):**
- [ ] <metric/claim 1>
- [ ] <metric/claim 2>
**Maintenance:** update here when facts change, then re-upload and re-index (re-indexing is mandatory).

---

## KB Content (Upload)

### <question-anchored header 1>
<2-4 sentences of spoken, paraphrasable substance.>

### <question-anchored header 2>
...
```

Typical sections for an own-product agent: who-the-company-is, how-it-is-set-up, what-it-does-in-<domain>, scale/effect (numbers, no prices), the-human-stays-in-the-lead, natural-conversation/concern-rebuttals, integrations, data-protection, secondary-use-case.

## Deploy handoff (recorded for vac-deploy)

The KB is attached at deploy. Record the intended config so `vac-deploy` can apply it:

- `usage_mode`: `auto` (RAG, on-demand). Use `prompt` only for content that must always be injected (counts toward context like the prompt — rare).
- `rag.embedding_model`: `e5_mistral_7b_instruct` default; the doc's index model MUST match this.
- `rag.optional_rag_enabled`: **default `true`** (LLM-gated, latency-optimized), set **`false`** when retrieval reliability dominates (the agent's core value is answering substantive questions and under-retrieval would break it). Decide per agent and record the choice + reason.
- `rag.max_vector_distance` 0.6, `max_documents_length` 50000, `max_retrieved_rag_chunks_count` 20 (defaults).

## Output

Write to the agent's directory:
- `knowledge-base.md` — meta block (local) + payload (uploaded)
- A **tier-1 spec** (inline note or a short block) telling `vac-prompt` what stays in the prompt's Answer Bank

## Quality Gate

Before handing off to vac-prompt:
- [ ] KB gate genuinely met (engaged decision maker + substantial long tail) — else NO KB, skip this step
- [ ] 6 boundary tests run; tier-1 (prompt) vs tier-2 (KB) split explicit
- [ ] tier-1 spec written for vac-prompt (high-frequency answers stay in the prompt)
- [ ] Payload in spoken paraphrasable German, question-anchored headers, no scripts/canned sentences
- [ ] Guardrail-taboo content EXCLUDED from payload (no prices/hard timelines/cost comparisons/named customers)
- [ ] Meta block has fact/number review flags for the human
- [ ] Payload > 500 bytes, meta/payload split clean (no meta in the upload section)
- [ ] Deploy config recorded (usage_mode, embedding_model, optional_rag_enabled + reason)
