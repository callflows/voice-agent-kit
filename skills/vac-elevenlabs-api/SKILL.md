---
name: vac-elevenlabs-api
description: ElevenLabs Conversational AI Agent API wrapper — full CRUD (Create, Read, Update, Delete) plus Outbound Calls. Direct API access against EU Residency endpoint.
---

# VAC ElevenLabs API (Full CRUD + Outbound Calls)

Direct access to the ElevenLabs Conversational AI API (EU Residency). Used by the `vac-deploy` skill, and available for read operations and outbound calls on its own.

## Allowed operations

| Operation | Method | Endpoint | Script |
|-----------|--------|----------|--------|
| Get Agent | GET | `/v1/convai/agents/{agent_id}` | `get_agent.py` |
| List Voices | GET | `/v1/voices` | `list_voices.py` |
| List Phone Numbers | GET | `/v1/convai/phone-numbers` | (inline curl) |
| Create Agent | POST | `/v1/convai/agents/create` | `create_agent.py` |
| Update Agent | PATCH | `/v1/convai/agents/{agent_id}` | `update_agent.py` |
| Delete Agent | DELETE | `/v1/convai/agents/{agent_id}` | `delete_agent.py` |
| Trigger Outbound Call | POST | `/v1/convai/twilio/outbound-call` | `outbound_call_with_vars.py` |
| Create KB Text Doc | POST | `/v1/convai/knowledge-base/text` | `create_kb_text.py` |
| Compute RAG Index | POST | `/v1/convai/knowledge-base/{id}/rag-index` | `compute_rag_index.py` |

## Requirements

- **Environment variable:** `ELEVENLABS_API_KEY` must be set
- **Python 3:** scripts use `urllib` (stdlib) or `requests`
- **ENV source (in order):** 1. `ELEVENLABS_API_KEY` already set in the environment → nothing else needed. 2. Otherwise load `.env` (`set -a && source .env && set +a`): in the repo it lives at `vac-skills/.env`, in the desktop bundle at the skill root. Check before every use: `python3 vac-elevenlabs-api/scripts/check_env.py` — it reports clearly whether the key is present and valid. **Note:** `vac/.env` is outdated (dead key, 401) — do not use it.

## API base

**Base URL (EU Residency):** `https://api.eu.residency.elevenlabs.io`

**Authentication:** `xi-api-key: $ELEVENLABS_API_KEY`

## Scripts

### Safety gates (apply to create / update / delete / outbound)

The writing scripts run **as a dry run when no flag is given**: they show what would happen and abort with exit 2. Only `--confirm` (or `--confirm-name` for DELETE) executes. **Binding rule: before setting the flag, ALWAYS obtain the user's explicit confirmation** — show the dry run output, ask, and execute only after a clear yes. Live deploys, PATCHes and outbound calls hit production, real people and real cost.

### create_agent.py (CREATE)

Creates a new agent from a finished config.json (including the real prompt text and a voice ID that is actually set).

```bash
python3 scripts/create_agent.py <config.json>            # dry run: shows name/voice/prompt length
python3 scripts/create_agent.py <config.json> --confirm  # deploys LIVE
```

Returns: `{"agent_id": "...", "main_branch_id": "...", "initial_version_id": "..."}`

### update_agent.py (UPDATE)

Updates an existing agent via PATCH.

```bash
python3 scripts/update_agent.py <agent_id> <patch.json>            # dry run: shows agent + fields
python3 scripts/update_agent.py <agent_id> <patch.json> --confirm  # patches LIVE
```

**Built-in no-clobber check:** if the payload contains a `prompt` block with prompt text but no `built_in_tools`, the script blocks (the PATCH would wipe system tools and KB/RAG from the live agent). The safe route: build the payload with `build_patch.py`. Deliberate overwriting only with `--allow-clobber`.

### build_patch.py (build a no-clobber payload)

Pulls the live config and replaces ONLY the prompt text — `built_in_tools`, `knowledge_base` and `rag` are guaranteed to survive. The standard route for every prompt iteration on an existing agent.

```bash
python3 scripts/build_patch.py <agent_id> --prompt <prompt.md> --out <patch.json>
```

Uses the `## Prompt (English)` section from `prompt.md`. Then run `update_agent.py` (dry run first, then `--confirm`).

### check_env.py (ENV check)

Checks whether `ELEVENLABS_API_KEY` is set and valid (auth test against `/v1/voices`, not `/v1/user`). Run it before the first API call of a workflow.

```bash
python3 scripts/check_env.py
```

### get_agent.py (READ)

Fetches an agent's full configuration. Used after every deploy to verify.

```bash
python3 scripts/get_agent.py <agent_id>
```

### delete_agent.py (DELETE)

Deletes an agent. Irreversible — the script forces confirmation: without `--confirm-name` it only shows what would be deleted; the name you pass must match the live name exactly.

```bash
python3 scripts/delete_agent.py <agent_id>                          # shows the agent, deletes NOTHING
python3 scripts/delete_agent.py <agent_id> --confirm-name "<name>"  # deletes (only after user confirmation!)
```

### list_voices.py (READ)

Lists available voices.

```bash
python3 scripts/list_voices.py [language]
```

### outbound_call_with_vars.py (RECOMMENDED for outbound calls)

**ALWAYS use this script for outbound calls.**

It pulls ALL dynamic variables from the agent config automatically and passes them along with the call.

```bash
python3 scripts/outbound_call_with_vars.py <agent_id> <phone_number_id> <to_number> [overrides_json]            # dry run
python3 scripts/outbound_call_with_vars.py <agent_id> <phone_number_id> <to_number> [overrides_json] --confirm  # places the call
```

**Input:**
- `agent_id` — the agent's ID
- `phone_number_id` — phone number ID (`phnum_xxx`)
- `to_number` — target phone number (E.164 format, e.g. `+49XXXXXXXXXXX`)
- `overrides_json` — (optional) JSON string with overrides

**What happens:**
1. GET agent → reads ALL `dynamic_variable_placeholders` as defaults
2. Merges defaults with overrides (overrides win)
3. Sends ALL variables in `conversation_initiation_client_data`

**Example:**
```bash
python3 scripts/outbound_call_with_vars.py agent_xxx phnum_xxx +49XXXXXXXXXXX \
  '{"call_ansprechpartner":"Herr Mueller"}' --confirm
```

### outbound_call.py (LEGACY — not recommended)

Low-level script. Passes ONLY the variables you name explicitly. Error-prone — variable drift is possible once the agent gains new variables and the outbound call script is not updated.

```bash
python3 scripts/outbound_call.py <agent_id> <phone_number_id> <to_number> [dynamic_variables_json]
```

Use it only if `outbound_call_with_vars.py` does not fit for some reason.

### create_kb_text.py (KNOWLEDGE BASE)

Uploads a text document into the workspace knowledge base. Called by `vac-deploy` when the build has a `knowledge-base.md`.

```bash
python3 scripts/create_kb_text.py "<doc-name>" <knowledge-base.md>
```

- Takes `knowledge-base.md` directly: uploads **only** the part after `## KB Content (Upload)` (the meta block stays local), and aborts if meta leaks through.
- Aborts if the payload is < 500 bytes (not RAG-indexable).
- Returns: `{"id": "...", "name": "...", "folder_path": [...]}` — the `id` is the `document_id` for the index step and the agent attach.

### compute_rag_index.py (KNOWLEDGE BASE)

Triggers the RAG index for a document and polls until `succeeded`.

```bash
python3 scripts/compute_rag_index.py <document_id> [model]
```

- `model` defaults to `e5_mistral_7b_instruct`. It **MUST** match `agent.prompt.rag.embedding_model`, otherwise retrieval does not kick in at runtime.
- Valid models: `e5_mistral_7b_instruct`, `multilingual_e5_large_instruct`, `qwen3_embedding_4b`.
- Polls at ~3s intervals until `status: succeeded`; aborts on `failed` / `rag_limit_exceeded` / `document_too_small` / `cannot_index_folder`.
- Attach + RAG config are set afterwards by `vac-deploy` in the agent PATCH (`prompt.knowledge_base` + `prompt.rag`), not by this script.

## Error handling

| HTTP code | Cause | Fix |
|-----------|-------|-----|
| `400` / `422` | Payload error | Check the JSON schema, check required fields |
| `401` | Invalid API key | Check `ELEVENLABS_API_KEY` |
| `403` | Missing permission | Add the permission in the ElevenLabs dashboard |
| `404` | Agent not found | Check the agent ID |
| `5xx` / timeout | API problems | Retry 3x max, then escalate |

## Rules

- **Use the EU endpoint:** `https://api.eu.residency.elevenlabs.io`
- **Umlauts spelled correctly:** ä, ö, ü, ß (no ae/oe/ue/ss in German output)
- **Protect secrets:** NEVER put the API key in code, logs or commits
- **Before DELETE:** always ask the user first (irreversible)
- **After CREATE:** always call `get_agent.py` to verify
