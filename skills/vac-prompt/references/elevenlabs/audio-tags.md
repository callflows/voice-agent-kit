# ElevenLabs Audio Tags — Reference for Eleven v3

## Overview

Audio tags are bracketed words that Eleven v3 interprets to steer emotion, delivery and non-verbal reactions. Format: `[tag_name]`, inline in the text.

**Model:** `eleven_v3_conversational` (for ConvAI agents)

## Tag Categories

### Emotions (base mood)

| Tag | Use |
|---|---|
| `[excited]` | Enthusiasm, positive energy |
| `[happily]` | Joy, satisfaction |
| `[sad]` | Sadness, sympathy |
| `[angry]` | Anger, firmness |
| `[sorrowful]` | Deep sadness, condolence |
| `[warmly]` | Warmth, cordiality — ideal for greetings |
| `[calmly]` | Calm, composure — ideal for de-escalation |
| `[concerned]` | Concern, empathy |
| `[reassuringly]` | Reassuring, giving confidence |

### Delivery Direction (tone/performance)

| Tag | Use |
|---|---|
| `[whispers]` | Quiet, confidential — for sensitive topics |
| `[shouts]` | Loud, forceful — use SPARINGLY |
| `[softly]` | Gentle, restrained |
| `[firmly]` | Firm, convincing — for clear statements |
| `[gently]` | Careful — for difficult news |

### Human Reactions (natural reactions)

| Tag | Use |
|---|---|
| `[laughs]` | Laughter — only on genuine humor |
| `[sighs]` | Sighing — understanding, relief |
| `[clears throat]` | Throat-clearing — topic change |

## Rules for ConvAI Voice Agents

### Mandatory tags (suggested_audio_tags in config.json)

Every agent MUST define at least these tags:

```json
"suggested_audio_tags": [
  {"tag": "warmly", "description": "For the greeting and positive moments. Max 1x per turn."},
  {"tag": "calmly", "description": "For de-escalation and reassuring statements."},
  {"tag": "excited", "description": "For positive reactions to caller interest. Sparingly."},
  {"tag": "firmly", "description": "For clear statements and important information."},
  {"tag": "sighs", "description": "For empathetic reactions when the caller is frustrated."}
]
```

### Governance in the prompt

Anchor these rules in the prompt under `# Audio Tags`:

1. **Max 1 tag per turn** — never several tags in one response
2. **Never consecutive** — not in back-to-back turns
3. **Never on data:** no tags on prices, dates, numbers, contact data. (Positioning/USP statements are NOT data and may carry `[firmly]`, see Optional moments.)
4. **Mandatory moments:**
   - Greeting: `[warmly]`
   - Sign-off: `[warmly]`
   - Caller hesitates or is frustrated: `[calmly]` or `[sighs]`
5. **Optional moments:**
   - Caller shows interest: `[excited]`
   - USP statement: `[firmly]`
   - Showing empathy: `[concerned]`

### Prompt example

```
# Audio Tags
Use audio tags to add natural emotion. Rules:
- Max 1 tag per turn. Never in consecutive turns.
- Never on data (prices, dates, numbers, contact data). Positioning/USP statements are not data and may take [firmly].
- Mandatory: [warmly] on greeting and final closing.
- On caller hesitation or frustration: [calmly] or [sighs].
- On positive engagement: [excited] (sparingly).
- Format: Place [tag] at the start of the sentence.
```

## Combinations (TTS only, not ConvAI)

In standard TTS, tags can be combined: `[happily][shouts] Wir haben es geschafft!`
For ConvAI agents: **use single tags only** (latency + naturalness).
