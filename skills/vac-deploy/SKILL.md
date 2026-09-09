---
name: vac-deploy
description: Deploy a voice agent directly to ElevenLabs and store artifacts in GitHub. Use after vac-review PASS. Handles voice selection, deployment via ElevenLabs API (EU Residency), and git commit/push.
---

# VAC Deploy

Deploy the agent directly to ElevenLabs. Store artifacts in GitHub. Output: `deployment-log.md`.

**HARD RULE: Deployment goes straight against the ElevenLabs API (EU Residency). The VAC Service is NOT used.**

## Prerequisites (input check)

Before starting, check that these files are present in the agent directory (`../voice-agents/<agent>/`):

| File | Comes from | Missing? |
|---|---|---|
| `prompt.md` (approved) | `vac-prompt` (step 4) | Run `vac-prompt` first |
| `config.json` (approved) | `vac-prompt` (step 4) | Run `vac-prompt` first |
| `example-variables.md` | `vac-prompt` (step 4) | Run `vac-prompt` first |
| `review-log.md` (PASS) | `vac-review` (step 5) | Run `vac-review` through to PASS; do not deploy without a PASS |
| `knowledge-base.md` | `vac-knowledge-base` (step 3b) | KB agents only; run `vac-knowledge-base` first |

If an input is missing, do NOT improvise and do NOT carry on with placeholders: name the missing predecessor step and ask the requester whether it should be done now.

## Process

1. Read approved `prompt.md`, `config.json`, `example-variables.md`
2. Select voice (if not already selected)
3. **Determine the use case** (`outbound` | `inbound`) — this drives the settings overlay. **Transfer target agents** (handed over via `transfer_to_agent`, no dialer of their own) fit neither overlay cleanly: no voicemail (never hits an answering machine), first_message is set (not empty), no custom variables. Workaround: pick `outbound`; the bundled `voicemail_detection` is then a no-op (verified example-internal). Record this deliberately in `deployment-log.md`.
4. Build the deploy payload via `apply_settings.py build` (merged settings baseline + use-case overlay + config.json, injects prompt text + voice ID)
4b. **(conditional) Knowledge base:** if `knowledge-base.md` exists → upload + rag-index + attach (see "Knowledge Base Deploy")
5. Deploy via ElevenLabs API (create new) or PATCH (update existing)
6. **Verify settings** via `apply_settings.py verify` (expected/actual against baseline + overlay), on top of the content verification
7. Write AGENT.md with the returned agent_id
8. Commit and push all artifacts to GitHub
9. Write `deployment-log.md`

## ElevenLabs API Connectivity

| Setting | Value |
|---|---|
| **Base URL (EU Residency)** | `https://api.eu.residency.elevenlabs.io` |
| **Auth Header** | `xi-api-key: $ELEVENLABS_API_KEY` |
| **Create Endpoint** | `POST /v1/convai/agents/create` |
| **Update Endpoint** | `PATCH /v1/convai/agents/{agent_id}` |
| **Get Endpoint** | `GET /v1/convai/agents/{agent_id}` |

**ENV setup:** `ELEVENLABS_API_KEY` must be set.

- **Order:** 1. Key already set in the environment (configured by the workspace admin) → done. 2. Otherwise load `.env`: in the repo it lives in `vac-skills/.env`, in the desktop bundle in the skill root — `set -a && source .env && set +a` from the respective directory. **`vac/.env` is obsolete** (dead key, 401). Verified 2026-06-29.
- **Check before the first API call:** `python3 ./vac-elevenlabs-api/scripts/check_env.py` — reports a clear OK, or what is missing and what to do about it.
- **Scope caveat:** The key can be missing individual scopes. Right now `user_read` is missing, so `GET /v1/user` returns a **401** even though the key is valid. That makes `/user` an unusable auth test. Check against `GET /v1/voices` or `GET /v1/convai/agents` instead (200 = ok). A 401 on `/user` alone does not mean a dead key.

## Settings Baseline (MANDATORY)

Agent-independent technical settings are **no longer** set by hand in the dashboard, but deterministically at deploy time. SSOT:

| File | Content |
|---|---|
| `references/settings/settings-baseline.json` | agent-independent settings (LLM, tools, ASR, turn, guardrails, bursting, file_input) |
| `references/settings/settings-outbound.json` | outbound overlay (eagerness `normal`, voicemail_detection, terse soft-timeout prompt) |
| `references/settings/settings-inbound.json` | inbound overlay (eagerness `eager`, patient soft-timeout prompt, no voicemail) |

The dividing line: **baseline/overlay = HOW the agent runs technically. config.json (vac-prompt) = WHAT it says.** Where they overlap, the settings layer wins. A single create/PATCH sets `conversation_config` **and** `platform_settings` together (empirically verified 2026-06-04).

**What the baseline guarantees (previously unset → ElevenLabs default or dashboard handiwork):**

| Setting | Value | Why it matters |
|---|---|---|
| `agent.prompt.llm` | `claude-haiku-4-5` (temperature 0.5, max_tokens -1, no reasoning) | without it explicit: the ElevenLabs default could change → wrong model with no warning |
| `agent.prompt.timezone` | `Europe/Berlin` | correct time references in the conversation (appointments, callback windows) |
| `tts.model_id` | `eleven_v3_conversational` | the API default `eleven_v3` is **forbidden** for DE agents (create throws 400) |
| `built_in_tools` | end_call, skip_turn (+voicemail outbound) | the tools array is regenerated server-side from this |
| `turn.turn_model` | `turn_v3` | newer than the live v2 — watch it on the first agent |
| `soft_timeout_config` | `use_llm_generated_message: true` + German override | without the override, ElevenLabs generates **English** filler in a German call |
| `guardrails` | focus + prompt_injection on | settable via API (see correction below) |
| `call_limits.bursting_enabled` | `false` | cost control |

**Bring an existing agent up to standard** (non-destructive — prompt/voice/variables are preserved):

```bash
python3 ./vac-deploy/scripts/apply_settings.py apply <outbound|inbound> <agent_id>
python3 ./vac-deploy/scripts/apply_settings.py verify <outbound|inbound> <agent_id>
```

**Another language?** The baseline ships English — prompts, summaries, filler phrases and
voicemail markers. `references/settings/LOCALIZATION.md` lists every field that has to
change, with the German production versions as a worked example.

## Deploy: Create New Agent

### Recommended path: `create_agent.py`

The wrapper script reads a finished config.json and issues the POST. **Safety gate:** without `--confirm` it runs as a dry run (shows name/voice/prompt length, deploys nothing). Show the dry-run output to the user, have them confirm explicitly, and only then pass `--confirm`.

```bash
python3 ./vac-elevenlabs-api/scripts/create_agent.py <deploy-config.json>            # dry run
python3 ./vac-elevenlabs-api/scripts/create_agent.py <deploy-config.json> --confirm  # LIVE
```

### Building the deploy config (via apply_settings.py)

The `config.json` from `vac-prompt` holds only the **content** (prompt placeholder, voice placeholder, dynamic variables, audio tags, first_message). The **technical settings** come from the settings baseline (see above). `apply_settings.py build` merges both and injects prompt text + voice ID:

```bash
python3 ./vac-deploy/scripts/apply_settings.py build <outbound|inbound> config.json \
  --prompt prompt.md --voice <selected_voice_id> --out .deploy-config.json
```

The script extracts the prompt text automatically from the `## Prompt (English)` section of `prompt.md`. The `.deploy-config.json` is temporary — delete it after the deploy (it holds a redundant copy of the full prompt).

### Raw cURL alternative (for debugging)

**⚠ Bypasses the safety gate:** no dry run, no confirmation, no no-clobber protection — the agent goes LIVE immediately. Only after an explicit yes from the user, and only if the wrapper scripts are unusable.

```bash
curl -X POST "https://api.eu.residency.elevenlabs.io/v1/convai/agents/create" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d @.deploy-config.json
```

## Deploy: Update Existing Agent

For updates to an existing agent. **⚠ The raw curl path bypasses the dry run and the no-clobber check** — prefer the wrapper script below; use curl only after an explicit yes and with a payload built by `build_patch.py`:

```bash
curl -X PATCH "https://api.eu.residency.elevenlabs.io/v1/convai/agents/$AGENT_ID" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d @.deploy-config.json
```

Or via the wrapper script (**safety gate:** dry run without `--confirm`; a built-in no-clobber check blocks prompt blocks that lack `built_in_tools`):

```bash
python3 ./vac-elevenlabs-api/scripts/update_agent.py <agent_id> <deploy-config.json>            # dry run
python3 ./vac-elevenlabs-api/scripts/update_agent.py <agent_id> <deploy-config.json> --confirm  # LIVE (after user confirmation)
```

## Knowledge Base Deploy (CONDITIONAL)

Only if the build has a `knowledge-base.md` (from `vac-knowledge-base`). Order: upload and index the KB first, then deploy/PATCH the agent with the doc ID + RAG config.

1. **Upload the payload** (only the `## KB Content (Upload)` part, extracted automatically):
   ```bash
   python3 ./vac-elevenlabs-api/scripts/create_kb_text.py "<agent>-kb" knowledge-base.md
   ```
   → returns the `document_id`.

2. **Compute the RAG index** (the model MUST match `agent.prompt.rag.embedding_model`):
   ```bash
   python3 ./vac-elevenlabs-api/scripts/compute_rag_index.py <document_id> e5_mistral_7b_instruct
   ```
   Polls until `succeeded`.

3. **Attach in the deploy config:** set inside the `conversation_config.agent.prompt` object:
   - `knowledge_base: [{"type":"text","name":"<agent>-kb","id":"<document_id>","usage_mode":"auto"}]`
   - `rag: {"enabled": true, "optional_rag_enabled": <true|false from vac-knowledge-base>, "embedding_model": "e5_mistral_7b_instruct", "max_vector_distance": 0.6, "max_documents_length": 50000, "max_retrieved_rag_chunks_count": 20}`

   Then create/PATCH as usual.

   **`optional_rag_enabled` fallback (PLAN-DEPENDENT):** Conditional RAG (retrieval only when the LLM needs it, a latency win) is not unlocked on every workspace plan. If it is not, create/PATCH throws **403 `feature_not_available`** with `param: agent.prompt.rag.optional_rag_enabled`. In that case **remove** the flag from the `rag` object and deploy again → standard RAG (always-on) takes over; once it is unlocked, catch up via a no-clobber PATCH (write back the complete live `prompt` block, otherwise you clobber built_in_tools/KB). Note it as a deviation in `deployment-log.md`. Workspace history: create on 2026-06-29 still 403, unlocked by ElevenLabs the same day and set to `true` via PATCH (example-internal).

4. **Verify:** `get_agent.py` → `prompt.knowledge_base` contains the doc ID, `prompt.rag.enabled = true`. Extend `deploy-verify.json` with the KB doc ID + rag.

**No-clobber on PATCH:** build the `prompt` block from the **live config** (it contains `built_in_tools`) and replace only the `prompt` text, `rag` and `knowledge_base` — otherwise system tools (voicemail_detection etc.) are lost (verified on the outbound build).

**Updating the KB later** = change the payload in `knowledge-base.md` → upload again (new doc ID) → re-index → re-attach the agent. A pure prompt iteration does NOT change the KB.

## Dynamic Variables (MANDATORY where variables are used)

**Every dynamic variable MUST have a sensible default value in `dynamic_variable_placeholders`.** No empty strings for variables referenced in the prompt or the first message.

```json
{
  "conversation_config": {
    "agent": {
      "dynamic_variables": {
        "dynamic_variable_placeholders": {
          "account_agent_name": "Lena",
          "account_name": "Example Staffing GmbH",
          "lead_first_name": "Peter"
        }
      }
    }
  }
}
```

For purely static agents (no variables): leave an empty object `{}`. Exception since 2026-07-05: `account_agent_name` is ALWAYS present on dispatched agents (the platform passes the account agent name on every call) — use a speakable default, not a marker.

## Response (Create)

```json
{
  "agent_id": "agent_xxx",
  "main_branch_id": "agtbrch_xxx",
  "initial_version_id": "agtvrsn_xxx"
}
```

| Field | Meaning |
|---|---|
| `agent_id` | ElevenLabs agent ID (universal identifier — reference it in `AGENT.md` as `el_agent_id`) |
| `main_branch_id` | branch ID for versioned editing |
| `initial_version_id` | first version of the agent |

## Post-Deploy Verification (MANDATORY)

**Settings** (automatic, expected/actual against baseline + overlay):

```bash
python3 ./vac-deploy/scripts/apply_settings.py verify <outbound|inbound> <agent_id>
```

Covers: llm, turn_model, turn_eagerness, speculative_turn, soft-timeout override, file_input, asr, tts.model_id, built_in_tools, guardrails, bursting. Exit 1 on any deviation.

**Content** (manual, via `get_agent.py` — the settings verification does not check this):
- [ ] `name` correct
- [ ] `first_message` correct (`""` for outbound, set for inbound)
- [ ] `language` = `de`
- [ ] `voice_id` set correctly
- [ ] `prompt` longer than the threshold (usually > 5000 chars) — evidence that the real prompt text was loaded, not the placeholder
- [ ] where variables are used: all `dynamic_variable_placeholders` filled
- [ ] (KB agents) `prompt.knowledge_base` contains the doc ID, `prompt.rag.enabled = true`, index `succeeded`
- [ ] (paying agents) no `transfer_to_agent`, `end_call` active

## What the Settings Step Sets Automatically (formerly dashboard handiwork)

Correcting an earlier assumption: **guardrails (`focus`, `prompt_injection`) ARE settable via API** and are now covered by the settings baseline — no longer set by hand in the dashboard. Empirically verified: a PATCH on `platform_settings.guardrails` takes effect.

## What Still Stays Manual (dashboard or a separate PATCH)

- Evaluation criteria (`platform_settings.evaluation.criteria`)
- Data collection schema (`platform_settings.data_collection`)
- **Custom** guardrails (free-text rules in `guardrails.custom`, not focus/prompt_injection)
- Versioning strategy

These settings survive iterations.

## Voice Selection

### Criteria

| Factor | Consideration |
|---|---|
| **Gender** | Match to agent persona (from briefing) |
| **Age** | Young/dynamic vs. mature/authoritative |
| **Energy** | High energy (sales) vs. calm (service) vs. professional (B2B) |
| **Accent** | Neutral standard German for the DACH market |
| **Model** | Always `eleven_v3_conversational` |

### Process

1. Check `references/elevenlabs/voices.md` for previously vetted voices
2. If the list is empty or the use case is new: run `vac-elevenlabs-api/scripts/list_voices.py de`
3. Pick a voice, document the rationale in `deployment-log.md`
4. For sibling agents (same customer, different campaign): deliberately pick a different voice so the campaigns stay distinguishable

## Error Handling

| Response | Action |
|---|---|
| 200 + `agent_id` | Continue with verification + AGENT.md + git |
| 400 / 422 | Payload error — check `config.json` (JSON schema, required fields) |
| 401 | `ELEVENLABS_API_KEY` invalid or missing. BUT: a 401 on `/v1/user` alone = missing `user_read` scope, not a dead key (cross-check against `/v1/voices`) |
| 403 `feature_not_available` (`param: …rag.optional_rag_enabled`) | Conditional RAG not in the plan. Remove the flag, deploy again (see KB deploy fallback) |
| 403 `feature_not_available` (model/TTS/ASR) | Feature not in the plan. Fall back in this order: `tts.model_id` → `eleven_flash_v2_5` (+ `expressive_mode: false`), `asr.provider` → drop it and take the default, `prompt.llm` → `gpt-5.4-mini` or `gpt-4o-mini`. Test each fallback on its own and record in the deployment log what deviates. |
| 403 (other) | Missing permission in the ElevenLabs dashboard |
| 5xx / timeout | Retry max 3x, then escalate |

## AGENT.md

Create it immediately after a successful deploy:

```markdown
# <Agent Name>

**Agent ID:** `<agent_id>`
**Platform:** ElevenLabs Conversational AI (EU Residency)
**Created:** <YYYY-MM-DD>
**Deployed via:** ElevenLabs API (direct)
**Agent URL:** https://elevenlabs.io/app/conversational-ai/agents/<agent_id>

## Voice
- **Name:** <voice name>
- **Voice ID:** `<voice_id>`
- **Language:** de
- **Model:** eleven_v3_conversational

## Configuration
- **first_message:** "..." (or `""` for outbound)
- **turn_eagerness:** eager / normal / patient
- **soft_timeout:** Xs
- **silence_end_call_timeout:** Xs
```

## Securing the Artifacts (optional)

```bash
cd ../voice-agents/
git pull --rebase
git add <agent-name>/
git commit -m "feat(<agent-name>): deployment - agent_id: <id>"
git push
```

## Output Format

Write `deployment-log.md`:

```markdown
# Deployment Log: <Agent Name>

**Date:** <date>
**Agent ID:** <agent_id>
**Voice ID:** <selected voice_id>
**Voice Name:** <voice name>
**Deployed via:** ElevenLabs API directly (EU Residency)

## Voice Selection
- **Selected:** <voice name> (<voice_id>)
- **Rationale:** <why this voice>
- **Alternatives evaluated:** <short list>

## Deployment
- **Status:** active
- **Endpoint:** POST https://api.eu.residency.elevenlabs.io/v1/convai/agents/create
- **Agent URL:** https://elevenlabs.io/app/conversational-ai/agents/<agent_id>
- **main_branch_id:** <branch_id>
- **initial_version_id:** <version_id>

## Verification (via get_agent.py)
- [x] Agent ID returned
- [x] Name correct
- [x] Language: de
- [x] first_message correct (empty for outbound, set for inbound)
- [x] Voice ID correct
- [x] Model: eleven_v3_conversational
- [x] Prompt: N characters
- [x] turn_eagerness correct
- [x] soft_timeout correct

## Git
- **Commit:** <hash>
- **Branch:** main

## Dynamic Variables for Integration
| Variable | Description | Default Value |
|---|---|---|
[Layer 2 + Layer 3 variables, if any]
```

## Outbound Call Triggering

After a successful deploy, outbound calls can be triggered directly through the ElevenLabs API:

```bash
python3 ./vac-elevenlabs-api/scripts/outbound_call_with_vars.py \
  <agent_id> <phone_number_id> <to_number> [overrides_json]
```

## Handoff to Testing

After successful deployment, inform the requester:
- Agent is live with `agent_id`
- Test scenarios are ready (from vac-test)
- Assign a test caller (named by the requester)
