# ElevenLabs Voice Agent Kit

A base configuration and a build pipeline that take you from a goal to a working voice agent
in ElevenLabs — without first spending a month learning which of the forty settings matter.

**Who this is for:** builders who want a phone agent that works, and anyone new to ElevenLabs
Conversational AI who would rather start from something proven than from an empty prompt box.

**What you get:** a production settings baseline you can deploy as-is, and a Claude skill pack
that runs the whole pipeline — briefing, conversation framework, prompt, quality review, deploy,
test. You give it the goal, it asks what it cannot infer, and hands you a live agent.

It is a starting point, not a platform. Campaign management, CRM integration and reporting
stay yours.

**→ [QUICKSTART.md](QUICKSTART.md): from a goal to a live agent in three steps.**

```bash
git clone https://github.com/callflows/voice-agent-kit.git
cd voice-agent-kit && ./install.sh
export ELEVENLABS_API_KEY="your-key"
```

Then open Claude Code and say what the agent should achieve — *"build me a voice agent that
calls dental practices and books a product demo"*. Claude asks what it cannot invent, runs
the pipeline, and hands you a deployed agent in your ElevenLabs workspace.

---

## 1. Base configuration

**[`elevenlabs-base-config.json`](elevenlabs-base-config.json)** — the settings block of a
production agent: model, TTS, turn-taking, ASR, guardrails and call limits.
German outbound, EU residency.

Prompt, voice and variables are deliberately **not** in there. That is where your work
belongs — the settings are the part you should not have to rediscover.

**[SETTINGS.md](SETTINGS.md)** explains every block, the trade-off behind it, and how to
apply the config via the API.

## 2. Skill pack for Claude

**[`skills/`](skills/)** — the method as a Claude skill bundle. It takes the base config
above, writes the prompt the way we ended up writing prompts, and deploys the result.

**This is not a platform and does not try to be complete.** It gets you from a goal to a
working agent quickly. Campaign management, CRM integration and reporting are yours.

Steps 1–6 are the path to a live agent. 7–9 are extras you can ask for afterwards:

| Step | Skill | Output |
|---|---|---|
| 0 | `vac-company-research` | company + use-case analysis |
| 1 | `vac-intake` | briefing |
| 2 | `vac-research` | conversation framework (SPIN, Challenger, Voss, MEDDPICC …) |
| 3 | `vac-design` | conversation architecture, 3-layer variables |
| 3b | `vac-knowledge-base` | knowledge base (optional) |
| 4 | `vac-prompt` | prompt + config + example variables |
| 5 | `vac-review` | 20-dimension scoring, hard-fail checklist |
| 6 | `vac-deploy` | live agent on ElevenLabs + verification |
| 7 | `vac-test` | test scenarios, transcript evaluation |
| 8 | `vac-task-extraction` | post-call task extraction prompt |
| 9 | `vac-campaign-goal` | campaign goal + typed outcomes |

Steps 7–9 are optional — Claude offers them after the deploy instead of running them.
| — | `vac-elevenlabs-api` | API wrapper (full CRUD, outbound calls) |
| — | `vac-update` | maintenance for agents already live |

### Install

**Claude Code** — one command:

```bash
git clone https://github.com/callflows/voice-agent-kit.git && cd voice-agent-kit && ./install.sh
```

That copies the bundle to `~/.claude/skills/voice-agent-kit`. Use `./install.sh --here` to
install it into the current project only.

**Claude Desktop** — grab `voice-agent-kit.zip` from the
[latest release](https://github.com/callflows/voice-agent-kit/releases/latest) and upload it
under Settings → Capabilities → Skills. Or build it yourself from a clone, which is always
current:

```bash
cd skills && zip -r ../voice-agent-kit.zip .
```

### Then

```bash
export ELEVENLABS_API_KEY="your-key"
# optional — defaults to EU residency:
export ELEVENLABS_API_BASE="https://api.elevenlabs.io"
```

Ask Claude *"build me a voice agent"* and it walks the pipeline, asking for the briefing
first. Start reading at `skills/SKILL.md`; `skills/GLOSSARY.md` explains the terms.

---

## Caveats — read these

- **The config is a starting point, not a recommendation.** Latency, turn-taking and
  guardrails are trade-offs. Measure them against your own calls, not ours.
- **English by default, German-tested.** The kit ships English prompts, summaries, filler
  phrases and voicemail markers. Everything in it was proven on German outbound calls, so
  some rules — formal address, number verbalization — are German habits worth checking
  against your language. `skills/vac-deploy/references/settings/LOCALIZATION.md` lists
  every field to change, with the German production versions as a worked example.
- **The skills are a working tool, not a product.** Opinionated, and they assume you have a
  campaign platform, a dispatcher and a CRM of your own. The kit deploys to ElevenLabs
  directly and leaves that plumbing to you.
- **No pattern database.** Our skills learn from build summaries of past agents. Those are
  customer data and are not included, so the pipeline starts from zero for you.
- **Live actions are gated.** Deploy, PATCH, outbound calls and delete run as dry-runs
  without an explicit `--confirm`. Keep it that way.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, sell what you build with it.

---

Built by [callFlows](https://callflows.de). Questions, corrections, war stories:
[Florian Lenz on LinkedIn](https://www.linkedin.com/in/florian-lenz-letsgetitdone/).
