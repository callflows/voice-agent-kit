# ElevenLabs Prompting Best Practices

Source: https://elevenlabs.io/docs/eleven-agents/best-practices/prompting-guide

## Prompt Structure

Separate sections with Markdown headings. Models are trained to pay particular attention to certain headings.

### Recommended Sections
- `# Personality` — who the agent is
- `# Goal` — what it should achieve
- `# Guardrails` — **special status**: models pay particular attention to this one
- `# Tone` — delivery and tonality

## Core Principles

1. **Short and concrete** — every instruction as terse as possible. Cut filler words.
2. **Emphasize critical rules** — "This step is important" at the end of the line. State the 1-2 most important rules twice (prompt + guardrails).
3. **Character Normalization** — email addresses, phone numbers and codes have a spoken format (for the user) and a written format (for tools/APIs).
4. **Give examples** — concrete sample dialogues improve reliability massively.
   > **This is where we deliberately deviate.** That holds for large models in chat. On the
   > phone you run on small, fast models, and they read an example as an instruction rather
   > than as an illustration — the agent then says the example sentence word for word in
   > every single call. See `../../SKILL.md` → "NEVER include sample dialogues". Describe
   > the move, never the sentence.
5. **Dedicated guardrails section** — all no-gos in one place under `# Guardrails`.

## Character Normalization

```
Spoken: "john punkt smith at company punkt com"
Written: "john.smith@company.com"

Spoken: "null eins sieben eins... zwei drei vier... fünf sechs sieben acht"
Written: "01712345678"
```

## Guardrails (Content Moderation)

Configurable per category since Feb 2026:
- sexual, violence, harassment, self-harm, profanity, religion/politics, medical/legal
- Thresholds: low / medium / high / off
- On false positives: raise the threshold, or clarify the context under the `# Guardrails` heading

## Voice & Turn Config

- `turn_timeout`: max wait for a response (default 7s)
- `turn_eagerness`: patient / normal / eager
- `silence_end_call_timeout`: silence before the call is ended
- TTS model: `eleven_v3_conversational` (recommended for natural conversations)
- `speculative_turn`: cuts latency, raises LLM cost

## Knowledge Base (RAG)

- Documents: TXT, PDF, URLs
- Short and focused (one topic per document)
- Clear headings help retrieval
- Worth it once the facts exceed 8,000 characters
- Embedding model: e5-mistral-7b-instruct

## Agent Transfer (Subagents)

- System tool "Transfer to AI Agent"
- Define handoff rules: when, and to which agent
- Transfer to a phone number is also possible
- Worth it when the conversation phases are cleanly separated
