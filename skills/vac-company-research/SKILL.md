---
name: vac-company-research
description: Research the calling/represented company from its website/domain. Dual role - (1) Step 0 auto-intake bootstrap when no human intake is available; (2) the DETAIL source for the agent's knowledge base. The few core facts + call purpose feed the prompt (tier-1); detailed company Q&A feeds the KB (tier-2, via vac-knowledge-base). Scrapes the company website for industry, products, target audience, brand voice, and prospect-level detail.
---

# VAC Company Research

Research a company automatically to generate the intake briefing for voice agent creation. This replaces the human intake step in the Auto Voice Pipeline.

**Dual role:** (1) auto-intake bootstrap (Step 0). (2) **Company-detail source for the KB** — invoked by `vac-knowledge-base` whenever a company-info KB is needed, even on the human-intake path. The split mirrors the KB boundary: **the few most-asked company facts + the call purpose → prompt (tier-1); detailed company questions → KB (tier-2).** When a KB is in play, do the deeper Step 4b pass below.

**Language note:** this skill is instruction text in English, but its output artifact `research-company.md` keeps German field labels and German industry values — it feeds a German-speaking voice agent, and downstream skills read those labels.

## Input

You receive a spawn prompt with:
- `firmenname`: Company name
- `website`: Company URL/domain
- `telefon`: Phone number (for the demo call)
- `ansprechpartner`: Contact person name (optional)
- `email`: Contact email (optional)

## Workflow

### Step 1: Website Scraping

Scrape the company website systematically:

```
1. Homepage → elevator pitch, Branche, Tonalitaet
2. /ueber-uns OR /about → company history, team, values
3. /leistungen OR /produkte OR /services → core products/services
4. /karriere OR /jobs → hiring signals, team size
5. /impressum → legal form, location, managing directors
```

Use `web_fetch` for each page. If a page 404s, skip it.
Use `web_search` for "[company name] [city]" to find reviews, news, industry context.

**Max 5 minutes on research.** Good enough beats perfect — the voice agent prompt will be iterated anyway.

### Step 2: Industry Classification

Classify into one of these verticals (match to closest):

| Vertical | Signale |
|---|---|
| PDL / Arbeitsvermittlung | Zeitarbeit, Personalvermittlung, Stellenangebote |
| Autohaus | Fahrzeuge, Werkstatt, Probefahrt |
| Arztpraxis / Gesundheit | Sprechzeiten, Terminbuchung, Fachrichtung |
| Handwerk | Meisterbetrieb, Gewerke, Notdienst |
| B2B Dienstleister | Beratung, Software, Agentur |
| B2B Vertrieb | Produkte, Aussendienst, Grosshandel |
| Sonstige | Fallback — describe the industry in free text |

The vertical names and the signal words stay German: they are the classification values written into the artifact, and the signals are what you actually look for on a German-language website.

### Step 3: Use Case Inference

Based on industry, infer the best demo voice agent use case:

| Vertical | Default Use Case | Agent-Rolle |
|---|---|---|
| PDL | Outbound candidate pitching | Calls companies, offers matching candidates |
| Autohaus | Inbound appointment setting | Takes calls, schedules test drives/workshop slots |
| Arztpraxis | Inbound Terminbuchung | Takes calls, books appointments |
| Handwerk | Inbound Auftragsannahme | Takes calls, captures the job |
| B2B Dienstleister | Inbound Qualifizierung | Takes calls, qualifies leads |
| B2B Vertrieb | Outbound Akquise | Calls prospects, books a meeting |
| Sonstige | Inbound Qualifizierung | Fallback |

### Step 4: Brand Voice Analysis

From the website text, extract:
- **Formalitaet:** Du/Sie? Casual or formal?
- **Energie:** calm/professional or energetic/young?
- **Schluesselwoerter:** 5-10 terms the company uses often
- **No-Gos:** obvious taboos (e.g. never name competitors)

### Step 4b: KB-Detail (only when a KB is needed — engaged-decision-maker agents)

Goes DEEPER than the 5-minute intake scrape. Read the product / how-it-works / use-case / cases / FAQ pages thoroughly. Gather the tier-2 substance an engaged prospect asks for:

- **Wie funktioniert das (Detail):** flow/steps, setup, integrations, technical key points.
- **Beispiele / Cases:** concrete applications per use case, success patterns that can be anonymized.
- **Zahlen / Metriken:** orders of magnitude, time saved, rates — **flag every number for review** (a human confirms before deploy).
- **Firmenhintergrund:** founding, location, team, values (made-in-Germany and the like).
- **Datenschutz / Compliance:** GDPR, server location, data processing agreement.
- **FAQ / typical objections + their answers.**

**Flag the taboos (NOT into the KB):** prices, hard delivery dates, cost comparisons, reference customers by name — capture them, but mark them clearly as "TABU, nicht in KB" so `vac-knowledge-base` excludes them (RAG would surface them). Price stays a prompt rule ("never quote one").

The 5-minute limit applies to the intake bootstrap, NOT to this KB-detail pass.

### Step 5: Output

Write `research-company.md`:

```markdown
# Company Profile: [Firmenname]

**Erstellt:** [date]
**Quelle:** [website URL]
**Branche:** [vertical]
**Use Case:** [type from Step 3]

## Firmenprofil
- **Name:** [Firmenname]
- **Branche:** [detailed]
- **Standort:** [city, region]
- **Groesse:** [if identifiable]
- **Kernprodukte/-services:** [bullet points]
- **USPs:** [what sets them apart?]
- **Zielgruppe:** [who are their customers?]

## Voice Agent Empfehlung
- **Use Case Typ:** [from taxonomy]
- **Richtung:** Inbound/Outbound
- **Agent-Rolle:** [1 sentence]
- **Primaerziel:** [e.g. book an appointment]
- **Sekundaerziel:** [e.g. capture contact data]

## Brand Voice
- **Anrede:** Du/Sie
- **Tonalitaet:** [description]
- **Schluesselwoerter:** [list]
- **No-Gos:** [list]

## Dynamische Variablen
- ansprechpartner_name: [name]
- firmenname: [name]
- [more depending on use case]

## KB-Detail (tier-2 -> vac-knowledge-base; only when a KB is needed)
> Everything above (core company profile + voice agent recommendation incl. call purpose) is **tier-1 -> prompt**. This block is **tier-2 -> KB**.
- **Wie funktioniert das (Detail):** [flow/steps/setup/integrations]
- **Beispiele / Cases:** [concrete, anonymizable]
- **Zahlen / Metriken:** [value] — [ ] to be confirmed by a human
- **Firmenhintergrund:** [founding/location/team/values]
- **Datenschutz:** [GDPR/server/DPA]
- **FAQ / Einwände:** [question -> answer keywords]
- **TABU (nicht in KB):** [prices/delivery dates/cost comparisons/customer names, if found]

## Recherche-Notizen
[summary of the key findings]
```

## Quality Gate

Before marking complete:
- [ ] Industry classified correctly
- [ ] Use case fits the industry
- [ ] Homepage + at least one further page scraped
- [ ] Brand voice has concrete traits (not generic)
- [ ] Output follows the template exactly

## Failure Modes

- **Website unreachable:** use `web_search`, build the profile from the search hits. Mark the quality as "eingeschraenkt".
- **Too little information:** build the profile anyway, using industry defaults. Mark clearly in the output what was assumed.
- **Foreign-language website:** analyze it anyway. The voice agent is built in German (DACH market).
