# No-Task-Logic — Worked Examples

Reference patterns for common agent types. Use these to calibrate how to translate an agent's primary goal into hard-exit vs. soft-exit logic.

The tables below are a **calibration reference** for the decision logic, not the output format. In the generated `task-extraction-prompt.md`, write the rules as a bulleted list (condition in bold → title pattern), not as a table — see the skill's "System Prompt Structure".

The pattern that's common across all of them: **a caller saying "no" is not automatically a hard exit.** Hard exit is when "no" comes with no information value AND no residual action. Soft exits — wrong person, competitor mentioned, callback requested, partial information captured — almost always still warrant a task because they reduce work for the next manual call.

---

## Example 1: Kontaktdaten-Verifikation

**Agent goal:** Verify whether stored contact data (email, phone, contact person) is still current.

**Expected fields:** correct email, correct phone, name of current AP.

| Caller behavior | Task? | Title pattern |
|---|---|---|
| AP confirms current data, all fields match CRM | **No** (`[]`) | — |
| AP says "my email changed to xyz@abc.de" | **Yes** | `Kontaktdaten aktualisieren: <Einrichtung>` |
| AP says "I'm not the right person anymore, ask Frau Schmidt" | **Yes** | `Kontaktperson aktualisieren: <Einrichtung> — neuer AP genannt` |
| AP not reached, gatekeeper says "she's back tomorrow" | **Yes** | `Rückruf morgen: <Einrichtung> — <AP-Name>` |
| Caller: "Wer sind Sie? Kein Interesse" — hangs up | **No** (`[]`) | — |
| Voicemail, no callback info | **No** (`[]`) | — |

**Why "kein Interesse" → no task:** the agent's goal is data freshness. If the caller refuses without correcting anything, the CRM state stays as-is and there is no actionable next step.

---

## Example 2: candidate pitching (Candidate Placement)

**Agent goal:** Place a specific candidate profile (e.g. "Krankenpfleger, 32, 8 Jahre Erfahrung") with a target company.

**Expected fields:** AP name + role, interest level (interested / not interested / wrong person / already using competitor), agreed next step (meeting, callback, send profile), competitor name if mentioned.

| Caller behavior | Task? | Title pattern |
|---|---|---|
| AP shows interest, agrees to meeting | **Yes** | `Termin vereinbaren: <Unternehmen> — <AP-Name>` |
| AP says "wrong person, my colleague Frau Meyer handles this, she's back tomorrow" | **Yes** | `Rückruf morgen: <Unternehmen> — Frau Meyer (Personal)` |
| AP says "we use a fixed agency already" | **Yes** | `Manuell nachfassen: <Unternehmen> — nutzt Agentur <Name wenn genannt>` |
| AP: "Schicken Sie mal Infos zu" | **Yes** | `Profil per Mail senden: <Unternehmen> — <E-Mail>` |
| AP: "Nein danke" — clear refusal, hangs up | **No** (`[]`) | — |
| Voicemail, no callback info | **No** (`[]`) | — |

**Why "competitor" → still a task:** the caller is qualified (they have the need), they are just not currently buying from us. A manual re-approach in 6 months is worth noting. The hard-exit is only the pure "no" with no information.

---

## Example 3: Cold outreach with open-ended need (e.g. Acme Leipzig)

**Agent goal:** Cold-call facilities to (1) identify the responsible person and (2) clarify whether the agent's service category (here: Arbeitnehmerüberlassung) is relevant.

**Expected fields:** facility name + location, AP name + role, direct phone or email, service-relevance status (currently using / used before / not relevant), demand details (qualifications, frequency), existing partners, objections.

| Caller behavior | Task? | Title pattern |
|---|---|---|
| Right AP, service actively used, asks for offer | **Yes** | `Angebot zusenden: <Einrichtung> — <E-Mail>` |
| Right AP, service not used but doors open | **Yes** | `Nachfassen perspektivisch: <Einrichtung>` |
| Wrong AP, but Durchwahl/email of right AP captured | **Yes** | `Ansprechperson direkt kontaktieren: <Einrichtung> — <Name>` |
| Right AP, "fixed partner" objection | **Yes** | `Angebot als Zusatzoption senden: <Einrichtung>` (briefing says: don't argue, position as additional option) |
| Right AP, "Rufen Sie später an" with concrete time | **Yes** | `Rückruf <Uhrzeit/Tag>: <Einrichtung>` |
| Caller: "Kein Interesse, bitte nicht mehr anrufen" | **No** (`[]`) | — |
| Gatekeeper blocks completely, no information | **No** (`[]`) | — |
| Voicemail, no callback info | **No** (`[]`) | — |

**Why "fixed partner" → still a task:** this briefing explicitly states "Nicht diskutieren. Angebot als zusätzliche Option positionieren." The agent's strategy treats fixed-partner facilities as future opportunities, so the colleague needs a task to send the offer materials.

---

## Cross-cutting principle

For every agent, ask: "If the colleague reading this task can take one concrete action that moves the lead forward, the task is worth creating. If they would only file it and forget — `[]`."

This filters out noise (pure refusals, dead voicemails, wrong-number calls) while keeping anything with residual value.
