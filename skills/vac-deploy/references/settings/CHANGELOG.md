# Settings Baseline Changelog

Changes to the agent-independent settings baseline (`settings-baseline.json` + overlays). They affect **all** new deploys (`apply_settings.py build`) and every existing agent brought up to standard via `apply_settings.py apply`. Drift from these values = bug.

## Agent LLM: `claude-haiku-4-5`

**Standard for all deploys.** The voice LLM is the single biggest lever on latency —
a small, fast model is worth more on the phone than a strong one.
If you want a different one, change `conversation_config.agent.prompt.llm` in the baseline and
the expected value in the `verify` check of `apply_settings.py`, so the two stay in sync.

**Baseline (`conversation_config.agent.prompt`):**
- `llm`: `claude-haiku-4-5`
- `temperature`: `0.5` (newly set explicitly)
- `max_tokens`: `-1` (new, unlimited)
- `reasoning_effort`: `null`, `thinking_budget`: `null` — no reasoning (otherwise API 400)
- `enable_reasoning_summary`: `false`

**`apply_settings.py`:** `verify` now additionally checks `temperature`, `max_tokens`, `enable_reasoning_summary`, `reasoning_effort`, `thinking_budget`. The expected LLM value is `claude-haiku-4-5` and must be changed together with the baseline.

**Left alone:** `data_collection.call_summary.llm` stays `gemini-2.5-flash` (analysis model, separate from the voice LLM).

**Live:** not pushed. Existing agents move to the new model on their next `apply`/`build`.

## 2026-06-10 — Data collection `call_summary` + German summary

**Trigger:** Customers review call results but should not have to read the transcript. A deterministic, customer-ready summary field was missing. Until now it was set per agent by hand in the dashboard (or not at all).

**New in the baseline (`platform_settings`):**
- `data_collection.call_summary` — string field with a German customer-facing prompt (3-5 sentences: reason for the call, statements/reaction, outcome + next steps; third person, no speculation, voicemail/abort in one sentence).
- `data_collection_scopes.call_summary = "conversation"`.
- `summary_language = "de"` — the native ElevenLabs summary in German too.

**Model choice:** per-field `llm` = `gemini-2.5-flash`. Rationale: the voice default `claude-haiku-4-5` is **not accepted** by ElevenLabs for analysis/data collection (400). `gemini-2.5-flash` is the cheapest permitted analysis model and identical to the workspace `analysis_llm`. Sonnet would add only marginal value on a short summary of a short transcript at ~8x the cost.

**`apply_settings.py`:** `apply` now also patches `data_collection`, `data_collection_scopes` and `summary_language`. `verify` checks `call_summary` (presence, llm, scope) + `summary_language`. On top of that: when switching away from a reasoning model (e.g. gpt-5.x), `reasoning_effort`/`thinking_budget` are set to `null`, otherwise 400 ("Reasoning effort is not supported for this LLM").

## 2026-06-05 — Initial settings baseline

**Trigger:** Technical settings were not being set deterministically. The deploy `config.json` (vac-prompt) held content only; LLM, tools, ASR, turn_model, guardrails, bursting and file_input came from ElevenLabs defaults or from dashboard handiwork. Risk: if ElevenLabs changed a default (e.g. the LLM), the next agent would silently get a different configuration.

**Newly created:**
- `settings-baseline.json` — SSOT for the agent-independent settings
- `settings-outbound.json` / `settings-inbound.json` — use-case overlays (deltas only)
- `scripts/apply_settings.py` — `build` (new agents) · `apply` (bring existing agents up non-destructively) · `verify` (expected/actual, exit 1 on deviation)

**Values set:**

| Area | Baseline | Outbound | Inbound |
|---|---|---|---|
| LLM | `claude-haiku-4-5` | | |
| timezone | `Europe/Berlin` | | |
| TTS model | `eleven_v3_conversational`, expressive_mode | | |
| Tools | end_call, skip_turn | + voicemail_detection | (no voicemail) |
| turn_model | `turn_v3` | | |
| speculative_turn | true | | |
| turn_eagerness | — | `normal` | `eager` |
| Soft timeout | LLM-generated, fallback "Mhm…" | terse DE override | patient DE override |
| file_input | false | | |
| Guardrails | focus + prompt_injection on | | |
| Bursting | false | | |

**Reasoned decisions:**
- `turn_eagerness` differentiated: outbound `normal` (avoids cutting people off in cold outreach), inbound `eager`. A deliberate latency trade-off (~100ms) in favour of naturalness.
- Soft-timeout overrides without few-shot examples (voice models parrot example sentences verbatim) and use-case specific.
- `optimize_streaming_latency` deliberately removed (deprecated).

**Empirically verified against the EU Residency API (throwaway probe agents + acme-outbound):**
- A single PATCH sets `conversation_config` **and** `platform_settings` (guardrails, bursting) together.
- `turn_v3` exists and is accepted (correction: live was previously running `turn_v2`).
- Guardrails ARE settable via API (the earlier doc assumption "not configurable" was wrong).
- `built_in_tools` as a full structure enables the tools and regenerates the `tools` array server-side.
- `prompt.timezone` is accepted in the create/update body.
- **Pitfall 1:** `soft_timeout_config.message` needs ≥ 1 character (empty → 400).
- **Pitfall 2:** `tts.model_id` must be set explicitly; the API default `eleven_v3` is forbidden for non-English agents (create throws 400).
- Prompt caching is active on native Haiku (visible in `charging.llm_usage`, ~82,500 cached tokens/call) → LLM TTFB median 310ms.

**Applied live:** acme-outbound-berlin (`agent_1001ks7…`, outbound) brought up to standard. 6 drifts fixed (turn_model, eagerness, soft-timeout override, file_input, bursting) + timezone. Content (17,857-character prompt, voice, variables, pronunciation dictionary, audio tags) preserved non-destructively. Verify: 15/15 PASSED.

**Open (researched, not implemented):** TTS `flash_v2_5` as a latency lever (~230ms, costs expressive_mode/audio tags) → needs an A/B test. `reasoning_effort` explicitly on `none` + a 1h cache TTL as a risk-free latency safeguard. Custom LLM via Azure rejected (cross-cloud hop GCP→Azure, loss of caching → slower, not faster).
