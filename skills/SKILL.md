---
name: voice-agent-kit
description: Build, change and ship ElevenLabs voice agents. Use this skill for anything voice-agent related — a new phone agent for a customer, changing an existing agent's behavior, opener or voice, a test call, or post-call task extraction. Runs a fixed pipeline from briefing to deployed agent.
---

# Voice Agent Kit — build and ship ElevenLabs voice agents

This bundle is a complete pipeline for building and maintaining ElevenLabs voice agents:
briefing → framework selection → conversation design → prompt → review → deploy → test →
post-call task extraction → campaign goal. It is written to be followed step by step, so
you do not need prior voice-AI experience to get an agent live.

The skills were extracted from a production German B2B setup — roughly 30,000 calls — and
genericised. Where a step assumes a campaign platform, a dispatcher or a CRM, that means
*yours*: the kit deploys to ElevenLabs directly and leaves the surrounding plumbing to you.
Terms you do not recognize → `GLOSSARY.md` in this directory.

**Language:** English throughout — the skills, the prompts they write, and what the agent
speaks. The method came out of German outbound calls, so a few rules (formal address,
number verbalization) are German habits; check them against your language. To run agents
in another language see `vac-deploy/references/settings/LOCALIZATION.md`.

**Path convention:** all relative paths in this document are relative to the root of this
bundle — the directory holding this `SKILL.md`. Change into it before running scripts.
Where an individual skill references `../../VOICE-AGENT-PROMPT-ARCHITECTURE.md`, the file
lives here in the bundle root.

**Artifacts:** each pipeline step writes files for one agent. Keep them together in one
directory per agent — `./voice-agents/<agent-name>/` is the convention the skills assume.
Where a skill writes `../voice-agents/<agent>/`, it means that agent directory.

## Setup (once)

You need an ElevenLabs account with Conversational AI and an API key:

```bash
export ELEVENLABS_API_KEY="your-key"
# optional, defaults to EU residency:
export ELEVENLABS_API_BASE="https://api.elevenlabs.io"
```

## Quick check at startup (always first)

1. Verify API access:
   ```bash
   python3 vac-elevenlabs-api/scripts/check_env.py
   ```
   If this fails → show the message and check the API key. STOP.
2. **Set the working directory:** artifacts belong in `./voice-agents/<agent-name>/`.
   If the directory does not exist, create it. If the project lives in Git, run
   `git pull --rebase` before doing any work, otherwise you edit against a stale state.


## The most common case: "build me an agent that does X"

The person has a goal and nothing else. In that case:

1. **Do not ask for a briefing — create one.** Run `vac-intake` and ask the questions
   yourself. Only ask what cannot be inferred; infer everything inferable and state the
   assumption instead of turning it into a question.
2. **Steps 1–6 are the route to a working agent.** At the end there is a deployed,
   verified agent in the ElevenLabs workspace. That is the goal of the first session.
3. **Do not tack on steps 7–9 unasked.** After the deploy, offer them rather than run
   them: test scenarios (7), task extraction (8), campaign goal (9).
4. **Summarise once before the deploy** — goal, audience, success criterion, voice — and
   ask explicitly whether it should go live. Only then set `--confirm`.

No campaign platform and no CRM is needed to get an agent live. No post-call webhook
either — that is too setup-specific and is deliberately not set here.

## What does the user want?

| Request | Route |
|---|---|
| **Build a new agent** | Run core path steps 1–6, order is binding (table below). Start: read and follow `vac-intake/SKILL.md` |
| **Change an existing agent** ("it gets X wrong", "adjust the opener", "swap the voice") | Read and follow `vac-update/SKILL.md` |
| **Test call** | `vac-elevenlabs-api/SKILL.md` → `outbound_call_with_vars.py` (mind the safety gate) |
| **Just a question/term** | `GLOSSARY.md` |

## Pipeline

**Steps 1–6 are the core path: briefing → deployed, working agent.** The order within it
is binding — every step needs the artifact of the previous one.

**Steps 7–9 are extras.** Offer them after the deploy, do not run them unasked. Anyone who
just wants a running agent quickly is done after step 6.

| Step | Skill folder | Output |
|---|---|---|
| 0 (optional) | `vac-company-research/` | research-company.md |
| 1 | `vac-intake/` | briefing.md |
| 2 | `vac-research/` | research.md |
| 3 | `vac-design/` | conversation-design.md |
| 3b (only on KB flag) | `vac-knowledge-base/` | knowledge-base.md |
| 4 | `vac-prompt/` | prompt.md + config.json + example-variables.md |
| 5 | `vac-review/` | review-log.md (min. 2 loops, minimum score 4.0, escalation after 3) |
| 6 | `vac-deploy/` | AGENT.md + deployment-log.md + deploy-payload.json + deploy-verify.json |
| 7 | `vac-test/` | test-scenarios.md |
| 8 | `vac-task-extraction/` | task-extraction-prompt.md (+ conditionally extraction-schema.json) |
| 9 | `vac-campaign-goal/` | campaign-goal.md + call-outcomes.json |

Run each step by reading and following the `SKILL.md` in the respective folder. Every
SKILL.md starts with an input check: if a predecessor artifact from the core path is
missing, do that predecessor step first, never improvise.

This pack does not claim to be complete. It gets you to a working agent quickly with a
proven base configuration and a proven prompt methodology. Everything beyond that —
campaign control, CRM integration, reporting — is yours.

## Safety rules (non-negotiable)

1. **Live actions only after an explicit yes.** Deploy, PATCH, outbound call and delete run
   as a dry run without a flag. Show the dry-run output to the user, ask clearly
   ("Should this go LIVE now?"), and only set `--confirm` after an unambiguous yes.
2. **No deleting without a double safeguard.** `delete_agent.py` requires the exact agent
   name. Always ask the user first. Deleting is irreversible.
3. **Change existing agents only via `vac-update`** (never "just quickly" via the API) — the
   skill enforces transcript evidence and the no-clobber PATCH.
4. **No price commitments, no invented facts** in agent prompts. Prompt rules are in
   `vac-prompt/SKILL.md`; when in doubt, ask the requester.

## Closing out every build/update

The live agent and the artifacts must never drift apart. So at the end of EVERY build or
update, right after successful verification, commit the artifacts of the agent directory —
to Git, if the project is versioned:

```bash
git add voice-agents/<agent-name>/
git commit -m "feat(<agent-name>): <what was built/changed> – agent_id: <id>"
```

If something fails → show the error message, do NOT guess.

In any case, summarise briefly in the chat: agent name, agent_id, what was changed/built.

## Roles

- **The requester** – the person in the chat. Answers briefing questions, confirms live actions.
- **Workspace admin** – whoever manages the ElevenLabs workspace and the API keys at your end.
