---
name: vac-research
description: Research and select conversation frameworks for voice agent builds. Use after intake to determine which sales/conversation frameworks best fit the use case. Draws from curated framework library and researches new frameworks when needed.
---

# VAC Research

Select and combine the right conversation frameworks for the use case. Output: `research.md`.

## Voraussetzungen (Input-Check)

Vor dem Start prüfen, ob diese Dateien im Agent-Verzeichnis (`../voice-agents/<agent>/`) liegen:

| Datei | Kommt aus | Fehlt sie? |
|---|---|---|
| `briefing.md` | `vac-intake` (Schritt 1) | Erst `vac-intake` ausführen |

If an input is missing, do NOT improvise and do NOT continue with placeholders: name the missing upstream step and ask the requester to supply it.

## Process

1. Read the `briefing.md` from Step 1
2. Load framework library from `references/frameworks/`
3. Match frameworks to use case type and objectives
4. If no existing framework fits → research new ones (web search)
5. Write `research.md` with selected frameworks and rationale

## Framework Library

Read from `references/frameworks/` — each file documents one framework:

| Framework | File | Best For |
|---|---|---|
| SPIN Selling | `references/frameworks/spin.md` | Complex B2B, consultative discovery |
| Challenger Sale | `references/frameworks/challenger.md` | Teaching-based, insight-driven sales |
| Beratungsansatz | `references/frameworks/beratungsansatz.md` | Short advisory calls, placement/recruiting |
| ARC Objection Handling | `references/frameworks/arc.md` | ALL agents (universal objection handling) |
| Chris Voss / Never Split | `references/frameworks/voss.md` | Labeling, mirroring, tactical empathy |
| Gong Research | `references/frameworks/gong.md` | Data-driven conversation patterns |
| MEDDPICC | `references/frameworks/meddpicc.md` | Enterprise qualification |

### Selection Matrix

| Use Case Typ | Primary Framework | Supporting | Always Include |
|---|---|---|---|
| `outbound-acquisition` | Beratungsansatz OR Challenger | Voss (labeling) | ARC |
| `outbound-service` | Beratungsansatz | Gong (patterns) | ARC |
| `inbound-qualify` | SPIN | Challenger (insights) | ARC |
| `inbound-service` | — (service-focused) | Voss (empathy) | ARC |
| `inbound-booking` | — (task-focused) | Gong (efficiency) | ARC |

ARC is ALWAYS included regardless of use case.

## When to Research New Frameworks

- Use case doesn't fit any existing framework well
- Briefing mentions a specific methodology you use
- Industry has specialized communication standards (e.g., medical, legal)

Research via web search. If a new framework is valuable, add it to `references/frameworks/` for future builds.

## Output Format

Write `research.md` in the agent's directory:

```markdown
# Research: <Agent Name>

**Briefing:** <link to briefing.md>

## Selected Frameworks

### Primary: <Framework Name>
- **Why:** <2-3 sentences rationale based on use case>
- **Key principles to apply:** <bullet list>
- **Adaptations needed:** <what to modify for this specific use case>

### Supporting: <Framework Name>
- **Why:** ...
- **Elements to use:** <specific techniques, not entire framework>

### Objection Handling: ARC
- **Anticipated objections:** <list based on use case>
- **Max loops:** 2 per objection, then graceful exit

## Framework Combination Strategy
How the selected frameworks work together. Which elements from each, how they sequence in the conversation.

## Patterns from Past Builds
<Relevant learnings from similar builds>
```

## Quality Gate

Before proceeding to Step 3 (Design):
- [ ] Frameworks selected with clear rationale
- [ ] Selection matches use case type from taxonomy
- [ ] ARC included
- [ ] Combination strategy defined (no conflicting principles)
- [ ] Past build patterns considered
