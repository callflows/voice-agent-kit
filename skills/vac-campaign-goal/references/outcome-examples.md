# Outcome Mapping — Worked Examples

Concrete goal definition + `call_outcomes` for common PDL agent types. Shows how a briefing's success definition is translated into goal text and typed outcomes. IDs here are placeholders (`uuid-N`) — generate real UUIDs in the actual artifact.

Both examples are no-sell outreach agents: the core is always whether external staffing support is relevant and who the right contact is for the human follow-up. They differ in their hook, and therefore in their primary goal.

**Scope reminder (see SKILL.md → SCOPE):** goal definition and outcomes only judge **calls that actually took place**. Voicemail, no answer, busy, technical drop and opt-out are handled deterministically by the campaign platform and do **not** appear as outcomes. The mandatory `failure` is always a genuine negative conversation result ("no need" / "not relevant"), never a voicemail or opt-out placeholder.

The goal text and the outcome labels below are written exactly as they go into the campaign platform: they are copy-pasted verbatim into an English-speaking campaign.

---

## Example A — cold outreach (general entry)

Briefing primary goal: gain usable market information OR identify the responsible contact person. Cleanly captured negative cases (no need) count as a valid result.

### campaign_goal (goal text)

> This goal definition evaluates only conversations that actually took place. Calls that never came about or broke off (voicemail, no answer, busy, technical error) as well as an explicit opt-out are handled deterministically by the campaign platform and are not subject to this evaluation.
>
> The goal of the campaign is cold outreach by phone and market research on behalf of our staffing provider at potential client companies. The agent establishes in a structured way whether external staffing support (temporary staffing, permanent placement, recruiting support) is relevant at the company called right now, was relevant in the past, or could become relevant later on, and identifies the responsible contact person along with a way to reach them for a human follow-up. The agent does not sell, does not quote prices and does not schedule appointments.
>
> A call is SUCCESSFUL if at least one of the following was achieved: a usable piece of market or needs information (current, past or future demand, relevant areas, qualifications sought, how often external staff is used, existing partners), or the responsible contact person together with a concrete way to reach them (direct line, email address or a callback time), or a cleanly captured route to the right person when the person reached was not the responsible one.
>
> The cleanly captured clean negative "not relevant at the moment", recorded after the follow-up questions have been worked through, counts as a valid result and is NOT scored as a failure.
>
> A conversation that took place is NOT successful when no usable information whatsoever, no pointer to a contact person and no way to reach anyone was obtained and the company called sees no need either.

### call-outcomes.json

```json
[
  { "id": "uuid-1", "label": "Needs/market info captured",                 "type": "success" },
  { "id": "uuid-2", "label": "Contact person + way to reach them secured", "type": "success" },
  { "id": "uuid-3", "label": "Route to the right person obtained",         "type": "follow_up" },
  { "id": "uuid-4", "label": "Fixed partners, open to future bottlenecks", "type": "follow_up" },
  { "id": "uuid-5", "label": "Callback window given",                      "type": "follow_up" },
  { "id": "uuid-6", "label": "Not relevant at the moment",                 "type": "failure" }
]
```

Mapping logic: "not relevant" is a valid `failure` (negative, but cleanly captured from a real conversation), not something to leave out. "Fixed partners, open" is `follow_up`, because a way in remains. No voicemail or opt-out outcome — the campaign platform catches those deterministically. No "Other" — `NO_MATCH` catches whatever is unclear.

---

## Example B — job ads (warm hook)

Briefing primary goal: clarify the vacancy status of the advertised role AND assess how relevant external support is. The hook is the specific ad, not a general staffing question.

### campaign_goal (goal text)

> This goal definition evaluates only conversations that actually took place. Calls that never came about or broke off (voicemail, no answer, busy, technical error) as well as an explicit opt-out are handled deterministically by the campaign platform and are not subject to this evaluation.
>
> The goal of the campaign is to call companies that have posted a specific job ad online, on behalf of our staffing provider. The hook is the published job ad. The agent clarifies whether the advertised role is still vacant, assesses whether external staffing support (permanent placement, temporary staffing, recruiting support) could be relevant in principle, records requirements and general conditions, and identifies the responsible contact person along with a way to reach them for a human follow-up. The agent does not sell, does not imply a hiring problem, does not quote prices and does not promise the availability of staff.
>
> A call is SUCCESSFUL if at least one of the following was achieved: the vacancy status of the advertised role is clarified (still open / no longer open), or the relevance of external staffing support is assessed (relevant, of interest later, or not relevant), or the responsible contact person is recorded with a concrete way to reach them, or usable requirements/qualifications or a further open need were named, or a clean route to the right person was obtained when the person reached was not the responsible one.
>
> Cleanly captured clean negatives count as valid results and are NOT scored as failures: the role has already been filled and there is no further need, or "external support is not relevant".
>
> A conversation that took place is NOT successful when no vacancy status, no relevance assessment, no requirements, no contact person and no way to reach anyone were obtained and the company called sees no need either.

### call-outcomes.json

```json
[
  { "id": "uuid-1",  "label": "Role vacant, relevance recognized, contact person + way to reach them secured", "type": "success" },
  { "id": "uuid-2",  "label": "Responsible contact person + contact details captured",                         "type": "success" },
  { "id": "uuid-3",  "label": "Further open need recognized (another role / recurring)",                       "type": "success" },
  { "id": "uuid-4",  "label": "Route to the right person obtained",                                            "type": "follow_up" },
  { "id": "uuid-5",  "label": "Of interest later / callback window given",                                     "type": "follow_up" },
  { "id": "uuid-6",  "label": "Info by email requested (email address captured)",                              "type": "follow_up" },
  { "id": "uuid-7",  "label": "Role already filled, no further need",                                          "type": "failure" },
  { "id": "uuid-8",  "label": "External support not relevant",                                                 "type": "failure" }
]
```

Mapping logic: the warm hook produces additional `success` results (a clarified vacancy status is already a partial win). Both `failure` cases are genuine negative conversation results ("filled, no need" / "not relevant"), not connection states. Voicemail, no answer and opt-out are deliberately absent — the campaign platform catches them deterministically.

---

## Rules of thumb from both examples

- **Real conversations only.** Goal definition and outcomes judge only calls in which someone actually spoke. Connection states (voicemail, no answer, busy, drop) and opt-out are handled deterministically by the campaign platform, not here.
- **Goal text first, outcomes second.** The outcomes are the discrete view of the same success definition.
- **`failure` = a genuine negative conversation result.** "Not relevant" / "no need" belongs in the list so that it is classified cleanly and recorded in the CRM. The mandatory `failure` is never a voicemail or opt-out placeholder.
- **`follow_up` = a way in remains.** Route to the right person, callback request, "of interest later", info by email wanted, fixed partners but open.
- **No catch-all.** The `NO_MATCH` fallback covers everything unmatchable.
