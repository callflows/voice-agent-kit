# Pipeline — single source of truth

Source of truth for the VAC pipeline skills. Skills are LLM instructions (Markdown), not code. Production execution runs either through the `vac` service (Claude Agent SDK spawns subagents) or interactively through Claude Code.

## Roles (instead of personal names)

Skills reference roles, never people:

- **The requester** — the person who requested the agent build/update and signs it off on the business side. Answers open briefing questions, names test callers, confirms live actions (deploy, outbound call, delete). In sales self-service this is usually the user themselves.
- **Workspace admin** — technical escalation: API keys, ElevenLabs workspace enablement, platform integration. Contacted when `check_env.py` fails or a workspace feature is missing.

Terms for non-specialists: `GLOSSARY.md` in this directory.

## Working directory & output convention

**Run skills from the skill root.** The skills read their own SKILL.md by path, not relative to the calling directory.

**Output artifacts belong in the agent directory:**

```
../voice-agents/<agent-name>/
```

One flat directory per agent. All build artifacts (briefing.md, research.md, conversation-design.md, knowledge-base.md, prompt.md, config.json, review-log.md, deployment-log.md, AGENT.md, test-scenarios.md, dossier-prompt.md, task-extraction-prompt.md, campaign-goal.md, call-outcomes.json, example-variables.md, deploy-payload.json, deploy-verify.json) end up there. No subfolders. `knowledge-base.md` only for KB agents (step 3b).

**Not here:**
- The skill directory itself contains only skill definitions, no build outputs.

## Skill pipeline (canonical)

| Step | Skill | Output file(s) |
|---|---|---|
| 0 | `vac-company-research` | `research-company.md` (optional) |
| 1 | `vac-intake` | `briefing.md` |
| 2 | `vac-research` | `research.md` |
| 3 | `vac-design` | `conversation-design.md` |
| 3b | `vac-knowledge-base` *(conditional)* | `knowledge-base.md` — only if `vac-design` flags "KB needed" |
| 4 | `vac-prompt` | `prompt.md` + `config.json` + `example-variables.md` |
| 5 | `vac-review` | `review-log.md` (≥ 2 loops) |
| 6 | `vac-deploy` | `AGENT.md` + `deployment-log.md` + `deploy-payload.json` + `deploy-verify.json` |
| 7 | `vac-test` | `test-scenarios.md` |
| 8 | `vac-task-extraction` | `task-extraction-prompt.md` (mandatory); conditionally `extraction-schema.json` (structured output schema). Historical exception: `dossier-prompt.md` (separate post-call dossier, so far only ai-ready-v3) |
| 9 | `vac-campaign-goal` | `campaign-goal.md` + `call-outcomes.json` (campaign goal definition + typed outcomes) |


## Pipeline doctrine (binding)

**The core path 1–6 is run in full and in this order** — every step needs the artifact of the previous one. Steps 7–9 are extras. Step 0 (`vac-company-research`) and step 3b (`vac-knowledge-base`) are **conditional**: 0 is optional, 3b only if `vac-design` flags "KB needed" (it then runs before `vac-prompt`). Everything else from step 1 onwards is mandatory. When the request is to build a new agent, the complete pipeline is run, not a subset.

- **The core path is steps 1–6.** No step within it is skipped: each one needs the artifact of the previous one. Steps 7–9 are extras and are only run on request.
- **The order is binding.** A later step may depend on an earlier one (e.g. `vac-task-extraction` reads `briefing.md`, `vac-deploy` reads the approved `prompt.md` + `config.json`). Pull a step forward only if the skill explicitly allows it.
- **This table is the only truth.** Where this SSOT and an individual SKILL.md contradict each other, the SSOT wins. Step numbers and output files follow this table, not diverging statements in the skills themselves.
- **Done means: every output file of steps 1–6 is in the agent directory.** If one is missing, the build is open, not "completed with reduced scope". Check off against this table before closing out.

### Skills outside the pipeline table
- `vac-update` — **maintenance skill** for EXISTING, already deployed agents (prompt fine-tuning, changing opener/voice/variable/tool). The counterpart to the new-build pipeline: that one runs once per agent, every later adjustment runs through `vac-update`. Enforces the three hard rules (evidence before edit → pull real transcripts; no-clobber PATCH straight against the ElevenLabs API EU residency; deploy and commit as one action). Orchestrates `vac-elevenlabs-api`, `vac-deploy`, `vac-review`. Not a pipeline step.
- `vac-elevenlabs-api` — tooling skill (Python scripts: `create_agent.py`, `get_agent.py`, `update_agent.py`, `list_voices.py`, `outbound_call*.py`). Called by `vac-deploy`, not a pipeline step of its own.

## What does NOT belong here

- Per-agent artifacts → `voice-agents/<agent>/` in the project, not in the skill directory

This bundle contains skill definitions (`<skill-name>/SKILL.md` + `references/`) and reference material.
