# Vetted Voices (DE) – proven in production

As of 2026-07-16. Source: the AGENT.md files of the deployed agents in `voice-agents/`.
These voices run in real campaigns and are therefore proven. For new agents pick from
here first; only if nothing fits: `vac-elevenlabs-api/scripts/list_voices.py de`.

| Voice ID | Name | Character | Used by |
|---|---|---|---|
| `c9tXABmaj4sESRRQ4Uqo` | Stefan Rank – Voice Agent Special | male, professional, sales-ready | general-pdl-* (3 agents), example-existing-contacts, vpl-job-ads-maschinenbau |
| `N8RXoLEWQWUCCrT8uDK7` | Emilia – Positive and Thoughtful | female, positive, considered | example-outbound, example-event-invite, example-inbound-in/outbound |
| `5HF8cmJxhR4X9DaQ7U3X` | Oscar – Warm and Charming | male, warm, charming | acme-outbound-berlin |
| `NkMe1eztMQReztnhYfeX` | Irene – Friendly and Approachable | female, friendly, approachable | acme-outbound-leipzig |

## Selection rules

- Always use the model `eleven_v3_conversational` (the API default `eleven_v3` throws a 400 for DE agents).
- Sibling agents (same customer, different campaign) get deliberately DIFFERENT voices so the
  campaigns are distinguishable on the phone (the one exception so far: general-pdl-* deliberately
  uses Stefan Rank throughout as its brand voice).
- Tried a new voice? Add it here after the first successful production deploy.
