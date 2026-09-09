# The base configuration, block by block

`elevenlabs-base-config.json` is the settings half of a production German outbound agent
(ElevenLabs Conversational AI, EU residency). Everything in it is a trade-off we landed on
after a lot of calls — not a universal recommendation. Read the reasoning, then decide.

Two placeholders must be filled before it runs:

| Placeholder | Where |
|---|---|
| `<<< HIER EUER PROMPT >>>` | `conversation_config.agent.prompt.prompt` |
| `<<< EURE STIMME >>>` | `conversation_config.tts.voice_id` |

---

## `conversation_config.agent` — model and prompt

```
llm: claude-haiku-4-5   temperature: 0.5      timezone: Europe/Berlin
```

A small, fast model on purpose. Latency is what makes a call sound artificial, and past
roughly a second and a half everyone hears the machine no matter how good the voice is.

The consequence people miss: **small models read prompt examples as instructions.** Write a
sample sentence into the prompt and the agent will say it verbatim on every call. Describe
the move, not the wording. That single rule changed our agents more than any setting here.

`built_in_tools` keeps empty descriptions on purpose — an empty description means the
ElevenLabs default, which is thorough and well-tuned. Writing your own short one replaces it
entirely and is usually a downgrade.

## `conversation_config.tts` — voice

```
model_id: eleven_v3_conversational      expressive_mode: true
```

Expressive, first chunk in roughly 250–400 ms. The alternative is
`eleven_flash_v2_5` with `expressive_mode: false` at 75–150 ms, but you lose audio tags.
We took expressiveness over the extra 200 ms; if your calls are transactional, flip it.

## `conversation_config.turn` — turn-taking

```
turn_model: turn_v3    mode: turn    turn_eagerness: normal
turn_timeout: 10s      silence_end_call_timeout: 30s      speculative_turn: true
```

The `soft_timeout_config` is the part worth stealing: after 3 seconds of silence the agent
emits one short filler, LLM-generated rather than a fixed phrase, capped at one per
generation. The override prompt tells it to reclaim the initiative in at most five words
**without** repeating or rephrasing the previous question — repeating is what makes an agent
sound like a broken machine.

## `conversation_config.asr` — recognition

```
provider: scribe_realtime    quality: high    audio: pcm_16000
```

`keywords` is empty and should not stay that way: put your product names, industry terms and
company names in there. It is the cheapest accuracy win available.

## `platform_settings.guardrails`

`focus` and `prompt_injection` on. Content filters deliberately **off** — in B2B cold calls
they fire on ordinary business language far more often than on anything real.
`synthetic_voice` detection is off here; enable it if voicemail loops are a problem for you.

The `version: "1"` field is mandatory. Without it the API answers `422 union_tag_not_found`,
which is not obvious from the error.

## `platform_settings` — after the call

```
analysis_llm: gemini-2.5-flash      summary_language: de      max_duration: 600s
call_limits: concurrency unlimited, 100k/day, bursting off
```

`data_collection.call_summary` holds the post-call summary prompt: 3–5 factual German
sentences aimed at the customer reviewing outcomes without reading transcripts.

**No post-call webhook is configured here** — where the result of a call goes is too
specific to your setup to ship as a default. But it is the seam that matters most:
**whatever you do with that payload decides whether you have a product or a demo.** Set it
up under `platform_settings.workspace_overrides.webhooks` once you know where the result
has to land. If it does not land in the system your customer already works in, you have
moved manual work rather than removed it.

---

## Applying it

Fill the three placeholders, then create the agent:

```bash
curl -X POST https://api.elevenlabs.io/v1/convai/agents/create \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d @elevenlabs-base-config.json
```

For EU data residency use `https://api.eu.residency.elevenlabs.io` instead. Patch an
existing agent with `PATCH /v1/convai/agents/{agent_id}` and only the blocks you want to
change — sending the whole document overwrites the prompt too.

The `_readme`, `_variablen_modell` and every other `_`-prefixed key are notes for humans.
The API ignores them; strip them if you prefer a clean payload.

## The variable model

Three levels, and the name carries the level:

| Level | Variables |
|---|---|
| Customer | `account_name`, `account_descriptor`, `account_address_city`, `account_agent_name` |
| Campaign | `campaign_profile` |
| Lead | `lead_company`, `lead_first_name`, `lead_last_name`, `lead_position`, `lead_phone_number` |

One rule, learned the hard way: **every placeholder needs a non-empty, speakable default.**
If dispatch delivers nothing, the raw value gets read out loud — and an agent saying
"Guten Tag, hier ist null" ends the call faster than any objection.
