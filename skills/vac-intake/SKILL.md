---
name: vac-intake
description: Structured intake and briefing for new voice agent builds. Use when starting a new voice agent project. Collects customer context, use case, target persona, call objectives, available data, and compliance requirements. Detects gaps and classifies the use case.
---

# VAC Intake

Collect and structure all information needed to build a voice agent. Output: `briefing.md`.

## Before Starting


## Mandatory Fields

Every briefing MUST contain all of the following. If information is missing, ask the requester (Auftraggeber:in) before proceeding.

### 1. Customer Context
- `customer`: Company name (your customer)
- `industry`: Industry (e.g., PDL, Autohaus, Arztpraxis)
- `region`: Geographic focus (default: DACH)
- `brand_voice`: Brand voice notes (formal/informal, energy level)

### 2. Use Case
- `use_case_type`: Classification from taxonomy (see below)
- `use_case_description`: What the agent does in 2-3 sentences
- `direction`: Inbound / Outbound / Both
- `call_context`: When/why is this call happening?

### 3. Target Persona
- `target_group`: Who is being called / who calls?
- `decision_maker`: Is this person the decision maker?
- `gatekeeper`: Is a gatekeeper likely? (receptionist, assistant)
- `pain_points`: Known pain points of the target

### 4. Call Objectives
- `primary_goal`: Primary conversion goal (e.g., Termin vereinbaren, Interesse wecken)
- `secondary_goals`: Secondary goals (e.g., Ansprechpartner identifizieren, Infos sammeln)
- `success_metrics`: How is success measured?

### 5. Available Data / Variables
- `dynamic_variables`: List of variables available at call time (from your campaign platform or the customer's system)
- `knowledge_base`: Documents/FAQs the agent should know
- `crm_integration`: What CRM data is available?

### 6. Compliance & Constraints
- `gdpr`: Data handling requirements
- `industry_rules`: Industry-specific regulations
- `no_gos`: Things the agent must NEVER say or do
- `escalation`: When and how to hand off to a human

## Use Case Taxonomy

Classify every new agent into one of these categories:

| Typ | Beschreibung | Beispiel |
|---|---|---|
| `outbound-acquisition` | Cold/warm outreach to prospects | candidate pitching, appointment setting |
| `outbound-service` | Proactive service calls | Terminerinnerung, Follow-up |
| `inbound-qualify` | Inbound lead qualification | Website-Anrufer qualifizieren |
| `inbound-service` | Inbound customer service | FAQ, Beschwerden, Status |
| `inbound-booking` | Appointment scheduling | Arztpraxis, Werkstatt |

## Output Format

Filled-in example: `references/briefing-example.md`.

Write `briefing.md` in the agent's directory (`../voice-agents/<agent-name>/briefing.md`):

```markdown
# Briefing: <Agent Name>

**Created:** <date>
**Use Case Type:** <from taxonomy>
**Direction:** Inbound/Outbound

## Customer Context
- **Customer:** ...
- **Industry:** ...
[all mandatory fields]

## Gaps & Open Questions
- [List anything that's missing or unclear]

## Similar Builds
- [Reference to similar past builds from learnings, if any]
```

## Quality Gate

Before proceeding to Step 2 (Research):
- [ ] All mandatory fields filled
- [ ] Use case classified
- [ ] No open gaps (or gaps explicitly accepted by the requester)
- [ ] Learnings from similar builds loaded
