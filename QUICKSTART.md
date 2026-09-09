# From a goal to a live agent

Three steps. Roughly twenty minutes, most of it Claude asking you questions it genuinely
needs answered.

## 1. Install

```bash
git clone https://github.com/callflows/voice-agent-kit.git
cd voice-agent-kit && ./install.sh
```

## 2. Set your key

```bash
export ELEVENLABS_API_KEY="your-key"
```

From the ElevenLabs dashboard → Profile → API Keys. The key needs Conversational AI
read/write. Add it to your shell profile so it survives a new terminal.

Outside the EU, also set:

```bash
export ELEVENLABS_API_BASE="https://api.elevenlabs.io"
```

Check it before you start:

```bash
python3 ~/.claude/skills/voice-agent-kit/vac-elevenlabs-api/scripts/check_env.py
```

## 3. Give Claude the goal

Open Claude Code in an empty directory and say what the agent should achieve. One sentence
is enough to start:

> Build me a voice agent that calls dental practices and books a slot for a product demo.

Claude then runs the pipeline. It will ask you for the things it cannot invent — who is
calling, what counts as success, what it must never say — and it will stop and ask rather
than guess. Expect roughly six rounds of questions.

At the end you get a deployed agent in your ElevenLabs workspace plus a directory of
artifacts (`voice-agents/<name>/`) holding the briefing, the conversation design, the
prompt, the review log and the deployment log.

---

## What actually happens

| Step | Skill | What it does | Asks you? |
|---|---|---|---|
| 1 | `vac-intake` | Turns your goal into a structured briefing | yes, the most |
| 2 | `vac-research` | Picks a conversation framework (SPIN, Challenger, Voss …) | rarely |
| 3 | `vac-design` | Conversation architecture, variables, objection handling | sometimes |
| 4 | `vac-prompt` | Writes the actual prompt + config | no |
| 5 | `vac-review` | Scores it across 20 dimensions, loops until it passes | no |
| 6 | `vac-deploy` | Picks a voice, deploys, verifies against the live agent | confirms before going live |

That is the whole path to a working agent — and where this kit stops caring about
completeness. Three more steps exist if you want them:

| 7 | `vac-test` | Test scenarios and transcript evaluation |
| 8 | `vac-task-extraction` | Post-call prompt that turns transcripts into CRM tasks |
| 9 | `vac-campaign-goal` | Campaign goal + typed outcomes for your dialer |

Ask for them when you need them: *"run the test scenarios"*. Claude will not run them
unprompted — the point is to get you calling, not to hand you nine documents.

## Making it actually call someone

The deployed agent is live but has no phone number attached. Two ways to use it:

**Test it in the browser** — ElevenLabs dashboard → your agent → Test. No number needed,
works immediately.

**Real calls** — buy or import a number in the ElevenLabs dashboard (Phone Numbers), then:

```bash
python3 ~/.claude/skills/voice-agent-kit/vac-elevenlabs-api/scripts/outbound_call_with_vars.py \
  agent_xxx phnum_xxx +49XXXXXXXXXXX --confirm
```

Or just ask Claude: *"call +49… with this agent"*. Without `--confirm` everything runs as a
dry-run — that safety gate is deliberate, keep it.

## If something breaks

| Symptom | Cause |
|---|---|
| `check_env.py` fails with 401 | Key wrong, or missing Conversational AI scope |
| Deploy returns `403 feature_not_available` | Your plan lacks a model, voice model or ASR provider from the baseline. Claude falls back automatically and notes what changed |
| Agent speaks English although you wanted German | `conversation_config.agent.language` — the prompt is written in English on purpose, the *language* field controls what is spoken |
| Agent repeats the same sentence every call | You put an example sentence in the prompt. Remove it. See the README |

## Cost

The kit itself is free. ElevenLabs Conversational AI is billed per minute by ElevenLabs and
telephony is billed on top — check their current pricing before you run a campaign. A few
test calls are cheap; a thousand-lead list is not.
