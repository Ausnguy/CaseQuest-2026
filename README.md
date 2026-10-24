# CaseQuest 2026

Team repository for **CaseQuest 2026**, a case competition sponsored by **ConocoPhillips** and hosted by the University of Houston's MISSO, FITP, and CougarCS organizations (October 23–24, 2026).

**Live prototype:** <https://casequest-2026.vercel.app>

## What this project does

Lone Mesa Energy is a fictional oil producer with six sites and eighteen machines (a transfer pump, a lift pump and a compressor at each site). In 2025 it lost about 6,599 hours to unplanned stops, and a quarter of that was machines sitting broken while someone waited for a spare part.

We recommend one fix: a **critical spare-parts program**, rolled out only at sites whose overdue safety actions are closed. To show how it would run day to day, we built a working system with three parts:

1. **A failure model** that reads each machine's daily vibration, temperature and inspection notes and flags the ones likely to have a bearing or seal failure in the next 3 days, with the parts that failure needs.
2. **Parvius, the manager's console** (web). It shows those alerts, tracks the parts warehouse, and lets the manager send an engineer with the right kits. A 3D map shows the sites, the machines and the engineers walking out to the job and back.
3. **The engineer's phone app** (Expo). The engineer gets the job, travels to the site by shaking the phone (or auto travel), starts the repair, ticks which kits were actually fitted, and heads back. Unused kits return to the warehouse.

The console and the phone share one live state through a small API on Vercel.

What the system never does:
- It never starts, stops or changes a machine. Only the engineer on site starts and finishes a repair.
- It never sends anyone by itself. The model only raises alerts; the manager decides who goes.
- It never sends an engineer without the parts. The server refuses unless every kit for the job is on the warehouse shelf.
- It never lifts a safety hold. Only a verified closure by an HSE supervisor does.

**Case and submission:** we act as consultants who pick the operational problem that matters most and recommend **one** practical solution, backed by the provided data and a prototype. Deck of 10 slides or fewer, 7-minute pitch, due Saturday Oct 24, 4:45 PM CT.

## Our recommendation

**A critical spare-parts program (Solutions option O4) at all six sites, rolled out gate-first.** Nothing is stocked at a site until its overdue severity-5 HSE actions are verified closed.

Why this problem and this solution (all from the 2025 data, see `docs/phase-3-fact-pack.md`):

- **313 unplanned events, about 6,599 hours of downtime, about $5.6M modeled lost contribution.**
- **24% of that downtime (1,613 hours) is machines waiting for parts.** Across the six sites, the share of breakdowns that wait tracks the empty share of the spare shelf almost exactly (r ≈ −0.995). Arroyo holds about 40% of the parts-wait hours (42% spare fill).
- Spares is the only option that cuts parts-wait, applies to every failure cause, and has no technology prerequisite. It never touches isolation, gas monitoring or restart steps.
- **The safety gate is the headline.** Mesa, Arroyo and Prairie each carry two overdue severity-5 actions (gas monitoring readiness, energy isolation), which block the pilot. Closing all six costs about $33k and 48 person-hours and unlocks about 76% of the benefit.
- **Modeled benefit:** about 968 avoided hours a year at steady state (range 565–1,210), 666 hours in year one if closures are verified by month 3. Cost: $168k upfront and $18k a year for spares, plus a $59.5k HSE backlog needed regardless. These are modeled from the Solutions sheet's reduction fractions, not promises.
- Condition monitoring at Arroyo is a costed **Phase 2**, not part of the ask.

Full reasoning, including how three blind AI grader agents ranked eight strategies (internal decision support, not human judges): `docs/phase-4-solution-selection.md`.

## The failure model

Code: `src/casequest/model.py` (prediction) and `src/casequest/maintenance.py` (parts plan). Tests: `tests/test_model.py`. Full write-up: `docs/model-card.md`.

**What it predicts.** Whether a machine will have a **mechanical failure (bearing wear or seal leak) within the next 3 days**, scored once per machine per day.

**What it does not predict.** Electrical trips, process upsets and unknown causes. In the days before those, the readings look like any normal day (vibration 1.15× normal against 2.1× before a bearing or seal failure), so no model on this data could warn about them, and ours does not claim to.

**Data it learned from.** Only the case's own workbook (`Dataset-Rules/`, cleaned into `data/processed/`). No outside data.
- `readings.csv`: 6,570 sensor readings, one per machine per day through 2025: vibration (mm/s), temperature (°C), operating state, data quality, the operator's inspection note, and when each reading was observed and received.
- `events.csv`: 385 stop events with start and end times and the cause (bearing wear, seal leak, electrical trip, process upset, unknown, scheduled service).
- `assets.csv`: each machine's normal vibration and temperature, used to turn raw readings into "times normal" and "degrees above normal".

**Features.** Five numbers per machine per day, using only readings already **received** by the end of that day (late-arriving readings are excluded, and a test checks this), so every score is what a planner could really have seen:

| Feature | Meaning |
|---|---|
| `vib_last` | Latest valid vibration, as a multiple of the machine's normal |
| `vib_max` | Highest valid vibration over the last 2 days, times normal |
| `temp_max` | Highest temperature over the last 2 days, °C above normal |
| `noise` | Operator "unusual noise" notes in the last 2 days |
| `gap` | 1 if there was no valid running reading in the last 2 days |

Only readings marked Valid and Running count as sensor evidence; noise notes count whatever the sensor quality. The 2-day window comes from the data: 91% of mechanical failures show vibration above 1.3× normal two days out, and 1% three days out.

**Label.** A day is positive if a bearing-wear or seal-leak stop starts within the following 3 days. Days when the machine is already stopped are left out (there is nothing to predict).

**Model and training.**
- Logistic regression on the five standardized features, fit with Newton's method and a small ridge penalty (our own ~20 lines of NumPy, no ML library).
- **Trained on Jan 1 – Jun 30, 2025:** 3,107 machine-days, 243 of them positive.
- **Tested on Jul 1 – Dec 31, 2025**, which training never saw: 3,152 machine-days, 273 positive.
- Alert threshold: the lowest score whose training precision reaches 50%. One alert level only; a lower "watch" band was tried and dropped because its days failed less often than average.
- Learned weights (standardized): latest vibration 0.95, noise notes 0.36, temperature 0.29, missing readings −0.34, 2-day max vibration −0.12. Latest vibration does most of the work.

**Results on the held-out half of 2025:**

| Measure | Value |
|---|---|
| AUC (machine-days) | 0.82 |
| Alerted days followed by a mechanical failure within 3 days | 68% (base rate 9%) |
| Mechanical failures with at least one alert before them | 90 of 91 |
| Median warning before the failure | 1.5 days |
| Failures warned early enough for a fresh parts order to land first | 82 of 91 |

This is scenario data with one reading per machine per day, so these numbers describe this dataset, not accuracy at a real site. [Petrobras 3W](https://github.com/petrobras/3W) (real offshore well events) would be the first outside check.

**From an alert to a job.** For each alerted machine, `maintenance.py` builds a plan: the likely cause (each machine type's 2025 split, 62–70% bearing and the rest seal, since the readings can't tell the two apart), a bearing kit and a seal kit for that machine type, the tools to take, and the site's open safety findings. `uv run python -m casequest.maintenance --export` writes every day's plans to `data/model/predictions.json`, which the console and phone read.

## How the prototype works

**Live:** <https://casequest-2026.vercel.app>

1. **Alert.** The console replays 2025 day by day, then runs a simulated live feed from Jan 1, 2026 (real 2025 episodes re-dated, clearly labelled SIMULATED). Each day the model's alerts appear on the Overview, the map, the asset panel and the Work board: likely cause, chance of failure within 3 days, the readings behind it, and the kits the job needs.
2. **Check stock.** The **Inventory** page is the manager's view of the warehouse: stock per kit and machine type, what is out with engineers, what today's alerts need, supplier restocks on the way, and every movement. If a kit is missing, the manager restocks it; the delivery lands after the sites' median 2025 parts wait (18 h, played at 3 s per hour). Starting quantities are modeled, because the workbook has no item-level stock.
3. **Send.** Acting as Manager, **Send engineer** becomes available once every kit is on the shelf. The engineer takes the kits from the warehouse beside the maintenance base and sets off.
4. **Repair.** The engineer travels to the site by shaking the phone (each shake is 0.5 km) or with auto travel, taps **Start repair**, ticks which kits were fitted (a repair does not always replace a part) and taps **Mark repaired**, then heads back. Kits not fitted go back on the shelf.
5. **Watch.** The 3D map shows supplier trucks arriving at the warehouse and each engineer walking out, working at the machine and walking back.

### Console pages

Every number is labelled **recorded** (solid outline) or **modeled** (dashed outline).

| Page | What it's for |
|---|---|
| **Map** | 3D map of the six sites: safety-hold cages, animated machines, spare-shelf cubes, avoided-hours towers, the warehouse and the engineers. The inspector on the right shows the field overview, a site (hold status, equipment, HSE approval workflow, open checks) or a machine (early warning, 60-day vibration chart, failure model, planner decision). Timeline lanes along the bottom show each site's stops and overdue critical checks. A six-beat story mode walks the pitch. |
| **Overview** | What's going on in plain English: sites on hold, machines down, predicted failures with Send engineer, what to do first. |
| **Work** | Safety checks to verify, readiness flags to decide, predicted failures, what's blocked behind a hold, and the field crew. |
| **Inventory** | The parts warehouse (see step 2 above). |
| **Trends** (`#/site/S04`) | One site's 2025 trends by day, week or month: vibration per machine, downtime by stage, parts-wait, period comparisons, causes and every stop. |
| **Briefings** | Why this problem, business case (rollout sliders reproduce 666 h year one and 968 h steady state), safety and guardrails (with a self-test), plan and KPIs. |

**Roles and guardrails.** "Acting as" (HSE supervisor, Planner, Manager) enforces the rules:
- A hold has no override; only a verified closure lifts it.
- Only an HSE supervisor can sign a closure. The sign-off needs a name, a witness, a date no later than today, an evidence note and a field-verification confirmation.
- Only the planner stages a kit, with a logged reason, and never at a held site.
- Only the manager restocks the warehouse and sends engineers.
- Every action lands in an append-only, exportable decision log.

**Parvis** is the briefing agent, in the right-hand analysis column and the `Ctrl K` command bar. It answers from the data with a rules engine (no LLM or API key) and never lifts a hold or authorizes work. Whisper handles speech input. Speech output uses Kokoro, an HD British voice that runs in the browser on WebGPU (Chrome or Edge, about 330 MB downloaded once), and falls back to the browser's own voices. Firefox and Zen on Linux have no WebGPU and only get voices if a speech engine such as espeak-ng is installed; with neither, the page says so and shows the text.

**Design.** Follows the "Parvius Operations" design file and its Industry system: Barlow Condensed headings, Barlow body, IBM Plex Mono labels, square hairline frames. Red means blocked or stopped, amber an early warning, green cleared.

### Run it

The live site needs no setup. Use Chrome or Edge for the HD voice.

Console and dispatch API together on a laptop:

```bash
cd web && npm install && npm run dev   # http://localhost:3300, in-memory store
```

Engineer phone app (Expo Go 57 on Android), always pointed at the live server:

```bash
cd mobile && npm run phone
```

With the phone on USB it opens in Expo Go by itself; otherwise scan the QR code on the same wifi. More detail: `prototype/README.md`, `web/README.md`, `mobile/README.md`.

The Streamlit "Parts Readiness Console" described in `docs/phase-5-product-design.md` is designed but not built; Parvius replaced it.

## Repository layout

| Path | What it is |
|---|---|
| `Dataset-Rules/` | Original dataset workbook (read-only, SHA-256 pinned) and the participant packet |
| `data/processed/` | Cleaned CSVs: assets, events, production, readings, sites, solutions, HSE |
| `data/model/` | `predictions.json`: the failure model's daily alerts and parts plans for the console and phone |
| `src/casequest/` | Cleaning, 39 integrity checks, metrics, option modeling, rollout roadmap, failure model, parts plan |
| `tests/` | Tests for cleaning rules, dataset integrity, analysis, the recommendation and the model |
| `docs/` | Phase write-ups, model card, cleaning log, reconciliation checks, fact pack, research, team plan |
| `prototype/` | Parvius console (`parvius.html`) and its field-work module (`fieldwork.js`) |
| `web/` | Vercel hosting for the console plus the dispatch API (warehouse, restocks, engineer jobs) |
| `mobile/` | Expo app for the field engineer's phone |

Docs, in reading order: `phase-1-discovery` through `phase-7-recommendation-costs-resources`, plus `model-card`, `cleaning-log`, `reconciliation`, `research-external`, `grader-reports`, `deck-outline` and `team-plan`.

## Rebuild the data, retrain and test

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv run python -m casequest.build                 # clean the raw workbook, run all checks, regenerate docs
uv run python -m casequest.factpack              # regenerate docs/phase-3-fact-pack.md
uv run python -m casequest.maintenance --export  # retrain the model and rewrite data/model/predictions.json
uv run pytest                                    # Python tests
cd web && npm test                               # dispatch and API tests
```

The raw workbook is never modified. Cleaning rules are logged in `docs/cleaning-log.md`, and the build refuses to write if an integrity check fails.

## Team

Austin Nguyen, Aayan Khan, Nick Shahbazian, Sidra Shaikh, Wali Lambert. Roles and the presentation split are in `docs/team-plan.md`.

---

*University of Houston | CaseQuest 2026*
