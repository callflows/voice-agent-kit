# ElevenLabs API Reference for the Voice Agent Builder

## Endpoints

Base URL (EU Residency): `https://api.eu.residency.elevenlabs.io`
Auth Header: `xi-api-key: $ELEVENLABS_API_KEY`

### Create an agent

```
POST /v1/convai/agents/create
Content-Type: application/json
```

```json
{
  "name": "Agent Name",
  "conversation_config": {
    "agent": {
      "prompt": {
        "prompt": "System prompt with {{variables}}..."
      },
      "first_message": "Greeting with {{agent_name}}...",
      "language": "de",
      "dynamic_variables": {
        "dynamic_variable_placeholders": {
          "firma_name": "Default company name",
          "agent_name": "Default agent name",
          "kandidat_vorname": ""
        }
      }
    },
    "tts": {
      "voice_id": "VOICE_ID",
      "model_id": "eleven_v3_conversational"
    },
    "turn": {
      "turn_timeout": 7,
      "silence_end_call_timeout": -1,
      "soft_timeout_config": {
        "message": "Sind Sie noch da?",
        "timeout_seconds": 15,
        "use_llm_generated_message": true
      }
    }
  }
}
```

**Dynamic variables:**
- Reference them in the prompt as `{{var_name}}`
- Set default values in `dynamic_variable_placeholders` (fallback when nothing is passed at runtime)
- Layer 2 variables (customer context) as defaults, layer 3 variables (call context) with an empty default
- Secret variables: `system__` prefix (never sent to the LLM, only used in tool headers)

Response: `{ "agent_id": "agent_xxx..." }`

### Outbound call (Twilio)

```
POST /v1/convai/twilio/outbound-call
Content-Type: application/json
```

```json
{
  "agent_id": "agent_xxx",
  "agent_phone_number_id": "phnum_xxx",
  "to_number": "+49XXXXXXXXXXX",
  "conversation_initiation_client_data": {
    "dynamic_variables": {
      "firma_name": "Müller Personalservice GmbH",
      "agent_name": "Nina",
      "kandidat_vorname": "Thomas",
      "kandidat_alter": "34",
      "kandidat_ausbildung": "Industriemechaniker mit Meisterbrief",
      "kandidat_erfahrung_gesamt": "12 Jahre",
      "kandidat_erfahrung_rolle": "6 Jahre als Schichtleiter",
      "kandidat_qualifikationen": "Meisterbrief, SPS-Programmierung",
      "kandidat_verfuegbar": "ab sofort",
      "job-ad_titel": "Schichtleiter Produktion (m/w/d)",
      "call_kontext": "job-ad"
    }
  }
}
```

**Important:** Runtime values override the defaults from agent create.

### Get an agent

```
GET /v1/convai/agents/{agent_id}
```

### Update an agent

```
PATCH /v1/convai/agents/{agent_id}
Content-Type: application/json
```

Body: same structure as create (changed fields only).

### Knowledge base

```
POST /v1/convai/agents/{agent_id}/add-to-knowledge-base
Content-Type: multipart/form-data

file: @document.txt
```

### Turn config

| Parameter | Default | Description |
|---|---|---|
| `turn_model` | `turn_v2` | Turn-taking model. `turn_v3` available (since 2026-02-09). |
| `turn_eagerness` | `normal` | `patient` / `normal` / `eager`. Outbound: `normal` (avoids cutting people off). Inbound: `eager`. |
| `speculative_turn` | false | Starts LLM inference speculatively before the final ASR result. Latency win; turn this off first when ASR acts up. |
| `turn_timeout` | 7 | Max wait for a reply (seconds) |
| `silence_end_call_timeout` | -1 | Silence before the call is ended (-1 = disabled) |
| `soft_timeout_config.message` | — | Fallback text. **Must be ≥ 1 character** (empty string → 400), even with `use_llm_generated_message: true`. |
| `soft_timeout_config.timeout_seconds` | -1 | Seconds until the soft timeout (-1 = disabled) |
| `soft_timeout_config.use_llm_generated_message` | false | The LLM generates the timeout message. **Without `llm_generated_message_prompt_override` the filler is English** — the override is mandatory for DE agents. |
| `soft_timeout_config.llm_generated_message_prompt_override` | null | Custom prompt for generating the filler. SSOT: the use-case overlays. |

**Mandatory for DE agents:** set `tts.model_id` explicitly to `eleven_v3_conversational` (or `eleven_flash_v2_5` / `eleven_turbo_v2_5`). The API default `eleven_v3` is **forbidden** for non-English agents and throws a 400 on create.

### Voices

Search for German voices via the voice library:
```
GET /v1/voices?language=de
```

Known IDs:
- Carla Voice: `<<< YOUR_VOICE_ID >>>`

### Guardrails (configurable via API)

**Correction:** Guardrails ARE settable via API (the earlier doc assumption "not configurable" was wrong, empirically disproven 2026-06-04). Path: `platform_settings.guardrails`.

```json
{
  "platform_settings": {
    "guardrails": {
      "focus": { "is_enabled": true },
      "prompt_injection": { "is_enabled": true },
      "content": {
        "execution_mode": "streaming",
        "config": { "sexual": {"is_enabled": false, "threshold": "medium"}, "...": "further categories" },
        "trigger_action": { "type": "end_call" }
      }
    }
  }
}
```

- `focus` — keeps the agent on topic. Use with care in cold outreach (can block legitimate sales turns). Define the prompt scope cleanly.
- `prompt_injection` — called "Manipulation" in the dashboard. Detects injection attempts.
- `content.*` — category filters (sexual, violence, harassment, …), off by default. `trigger_action.type` `end_call` hard-ends the call on a violation (risk on a false positive: dead line). Consider `retry`/`transfer` when enabling it.
- Known false-positive issue: the Carla widget agent on sexual/religious content (CAL-65).


### Built-in system tools

Enabled via `conversation_config.agent.prompt.built_in_tools` (the old `tools` array was removed in July 2025; it is regenerated server-side from `built_in_tools`). Every tool key carries a `SystemToolConfig` object:

```json
"built_in_tools": {
  "end_call": { "type": "system", "name": "end_call", "params": {"system_tool_type": "end_call"}, "response_timeout_secs": 20, "...": "further defaults" },
  "skip_turn": { "...": "same shape" },
  "voicemail_detection": { "params": {"system_tool_type": "voicemail_detection", "voicemail_message": ""}, "...": "same shape" }
}
```

`voicemail_detection` is outbound-only. Full structure: see `references/settings/settings-baseline.json`.
