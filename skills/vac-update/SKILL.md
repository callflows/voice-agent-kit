---
name: vac-update
description: Use this skill when something on an already existing, live ElevenLabs/11labs voice agent under voice-agents/<agent>/ needs to be changed and the change then deployed/rolled out/pushed live/patched. This is the skill for "change + roll out" on an existing agent — whether that means rewording the prompt, softening the opener/first message, tightening a guardrail, making a transfer condition stricter, adding a dynamic variable, swapping the voice, or adjusting a tool or persona. It also applies to phrasings like "the agent transfers too early, make the condition stricter and push it live", "adjust the prompt of <agent> and deploy", "the customer wants X changed, roll it out", "it does Y wrong, fix that". Observed misbehavior or a customer request counts as a trigger. NOT for a new agent from scratch (use the vac build pipeline starting at vac-intake), NOT for merely auditing/evaluating calls, campaigns, extraction quality or success rates. Enforces the ground rules: pull real transcripts as evidence first, then a no-clobber PATCH straight against the ElevenLabs API (EU Residency, no VAC service), verify, document, and treat deploy = commit = push as ONE action.
---

# VAC Update — patching existing agents

Changes an **already deployed** agent. No rebuild. The canonical build pipeline
(`vac-intake` → … → `vac-deploy`) runs exactly once per agent; every later change
goes through this skill.

**Why a separate skill:** an ad-hoc edit on the live agent easily breaks three rules
distilled from real builds — changing without evidence, clobbering tools/KB in the PATCH,
or deploying without committing. This skill turns those rules into the path.

> **Prompt architecture foundation:** `../../VOICE-AGENT-PROMPT-ARCHITECTURE.md` (rule vs. goal,
> 4-layer model). **Deploy mechanics/settings:** `../vac-deploy/SKILL.md`. **API scripts:**
> `../vac-elevenlabs-api/SKILL.md`. This skill orchestrates those, it does not duplicate them.

## The three hard rules (non-negotiable)

1. **Evidence before edit.** Before changing a prompt, pull and analyze real 11labs transcripts
   of that agent. A prompt change with no evidence from real calls is a guess, not a fix. (Step 1)
2. **Opener rule (outbound).** An outbound agent ALWAYS delivers the defined opener as its first
   turn, no matter what the person called says first. Every change to the first message/opener
   is checked against this rule. (Step 2)
3. **Deploy = commit = push, one action.** A live deployment without committed artifacts is drift:
   repo and live agent diverge. After successful verification you commit and push immediately,
   not "later". (Step 6)

## Procedure

### Step 0 — locate the agent & load the live state
- Agent directory: `../voice-agents/<agent>/`. Read `agent_id` from `AGENT.md`.
- ENV: if `ELEVENLABS_API_KEY` is already in the environment → done. Otherwise load `.env`
  (`.env` in the skill root): `set -a && source .env && set +a`
  from the respective directory (`vac/.env` is dead). Check with
  `python3 ../vac-elevenlabs-api/scripts/check_env.py` (tests against `/v1/voices`, not `/v1/user`).
- **Pull the live config** (the basis for the no-clobber PATCH):
  ```bash
  python3 ../vac-elevenlabs-api/scripts/get_agent.py <agent_id> > .live-config.json
  ```

### Step 1 — pull evidence (MANDATORY before every prompt edit)
```bash
python3 ./scripts/fetch_transcripts.py <agent_id> --limit 10 --out ../voice-agents/<agent>/transcripts-evidence.md
```
Read the transcripts and name the concrete failure point: where does the agent fail, in which
turn, with which wording? That is the justification for the change. For pure non-prompt changes
(swapping the voice, setting a variable default) the evidence requirement is relaxed — then note
briefly in the change rationale that no transcript analysis was needed, and why.
`transcripts-evidence.md` is a working artifact and is NOT committed (only the analysis counts).

### Step 2 — edit the artifacts
- What gets edited are the source artifacts in the agent directory, NOT the live config directly:
  `prompt.md`, `config.json`, and where applicable `conversation-design.md`, `example-variables.md`.
- **Respect the prompt architecture:** pick the right layer (guardrail = hard rule only where
  irreversible/legal/brand; style = goal definition + latitude). See the base document.
- **Opener rule** (see above) to be checked on every first message/opener change.
- **Review gate:** if the change is substantial (prompt structure, guardrails, conversation goal,
  persona), run the `vac-review` skill against the changed `prompt.md` — minimum score 4.0, append
  the result to `review-log.md`. Trivial edits (typo, one sentence, a variable default) need no full
  review; note that in the change rationale.

### Step 3 — build the PATCH (no-clobber) & deploy
**HARD RULE: the PATCH goes straight against the ElevenLabs API (EU Residency). The VAC service is
NOT used.**

**No-clobber is mandatory — and automated.** A partial PATCH without the complete `prompt` block
wipes `built_in_tools` (end_call, voicemail_detection, transfer_to_agent) and
`knowledge_base`/`rag` server-side. So build the payload according to the type of change:

- **Case A — only the prompt text changed (the standard case):** `build_patch.py` pulls the live
  `prompt` block and replaces only the text — tools/KB/RAG are guaranteed to survive:
  ```bash
  python3 ../vac-elevenlabs-api/scripts/build_patch.py <agent_id> \
    --prompt ../voice-agents/<agent>/prompt.md --out .patch.json
  ```
- **Case B — config.json/settings changed (voice, variables, first_message, overlay):** build the
  deploy config through the settings mechanics of `vac-deploy`:
  ```bash
  python3 ../vac-deploy/scripts/apply_settings.py build <outbound|inbound> \
    ../voice-agents/<agent>/config.json \
    --prompt ../voice-agents/<agent>/prompt.md --voice <voice_id> --out .patch.json
  ```
- **Case C — a pure tool toggle:** merge PATCH on `built_in_tools` —
  send only the tool keys that changed.

Deploying (**safety gate:** show the dry run first, have the user confirm, then `--confirm`;
the built-in no-clobber check additionally blocks unsafe payloads):
  ```bash
  python3 ../vac-elevenlabs-api/scripts/update_agent.py <agent_id> .patch.json            # dry run
  python3 ../vac-elevenlabs-api/scripts/update_agent.py <agent_id> .patch.json --confirm  # LIVE
  ```
- Delete `.patch.json` and `.live-config.json` after the deploy (temporary, they hold the full
  prompt redundantly).

### Step 4 — verify live (MANDATORY)
```bash
python3 ../vac-deploy/scripts/apply_settings.py verify <outbound|inbound> <agent_id>   # settings
python3 ../vac-elevenlabs-api/scripts/get_agent.py <agent_id>                          # content
```
Check: did the changed fields land live? Is the prompt length plausible (> threshold, no
placeholder)? Are `built_in_tools` and `knowledge_base` STILL there (proof that nothing got
clobbered)? Is `first_message` correct (`""` outbound / set inbound)? Update the result in
`deploy-verify.json`.

### Step 5 — bring docs & learnings up to date
- `deployment-log.md`: append a new update entry (date, what changed, evidence rationale,
  verification result). Keep old entries — the log is history.
- `AGENT.md`: update only when key values changed (voice, first_message, turn_eagerness).

### Step 6 — deploy = commit = push (one action)
Immediately after successful verification, not later:
```bash
cd ../voice-agents/
git pull --rebase
git add <agent>/          # do NOT commit transcripts-evidence.md
git commit -m "fix(<agent>): <what changed> — <short evidence rationale>"
git push
```
`voice-agents/` is part of the `vac-platform` repo (one repo). Commit message rules (Author
trailer etc.) as customary in the repo.

## Final checklist
- [ ] Transcripts pulled + failure point named (or the evidence exception justified)
- [ ] Opener rule checked (on a first message change)
- [ ] Review gate passed (on a substantial change)
- [ ] No-clobber PATCH deployed, tools/KB still present live
- [ ] Settings + content verification green
- [ ] `deployment-log.md` / where applicable `AGENT.md` / `deploy-verify.json` updated
- [ ] Committed + pushed, `.patch.json`/`.live-config.json`/`transcripts-evidence.md` not in the commit

## Error handling
Inherits the tables from `vac-deploy` and `vac-elevenlabs-api` (400/401/403/404/5xx). Notably:
- **401 on `/v1/user` only** = missing `user_read` scope, not a dead key. Check against `/v1/voices`.
- **403 `feature_not_available` (`…rag.optional_rag_enabled`)** = conditional RAG not in the plan.
- **PATCH 200, but a tool is gone** = silently stripped (workspace feature not enabled, e.g.
  `transfer_to_agent`) OR clobbered (incomplete `prompt` block). `get_agent.py` reveals both.
