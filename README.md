# CaseQuest 2026

Team repository for **CaseQuest 2026**, a case competition sponsored by **ConocoPhillips** and hosted by the University of Houston's MISSO, FITP, and CougarCS organizations (October 23–24, 2026).

**Case:** Lone Mesa Energy, a fictional oil producer with six sites and eighteen pieces of equipment, is losing production to equipment failures, maintenance delays, spare-parts shortages and safety gaps. We act as consultants: pick the operational problem that matters most and recommend **one** practical solution, backed by the provided data and a working prototype.

**Submission:** Saturday Oct 24, 4:45 PM CT. Deck of 10 slides or fewer, 7-minute pitch, prototype submitted alongside.

## Our recommendation

**A critical spare-parts program (Solutions option O4) at all six sites, rolled out gate-first.** Nothing is stocked at a site until its overdue severity-5 HSE actions are verified closed.

Why this problem and this solution (all from the 2025 data, see `docs/phase-3-fact-pack.md`):

- **313 unplanned events, about 6,599 hours of downtime, about $5.6M modeled lost contribution.**
- **24% of that downtime (1,613 hours) is machines waiting for parts.** Across the six sites, the share of breakdowns that wait tracks the empty share of the spare shelf almost exactly (r ≈ −0.995). Arroyo holds about 40% of the parts-wait hours (42% spare fill).
- Spares is the only option that cuts parts-wait, applies to every failure cause, and has no technology prerequisite. It never touches isolation, gas monitoring or restart steps.
- **The safety gate is the headline.** Mesa, Arroyo and Prairie each carry two overdue severity-5 actions (gas monitoring readiness, energy isolation), which block the pilot. Closing all six costs about $33k and 48 person-hours and unlocks about 76% of the benefit.
- **Modeled benefit:** about 968 avoided hours a year at steady state (range 565–1,210), 666 hours in year one if closures are verified by month 3. Cost: $168k upfront and $18k a year for spares, plus a $59.5k HSE backlog needed regardless. These are modeled from the Solutions sheet's reduction fractions, not promises.
- Condition monitoring at Arroyo is a costed **Phase 2**, not part of the ask. A readiness flag (vibration above 1.3× normal or an operator noise note) only suggests which kit to pre-stage, and a person always decides.

Full reasoning, including how three blind AI grader agents ranked eight strategies (internal decision support, not human judges): `docs/phase-4-solution-selection.md`.

## Repository layout

| Path | What it is |
|---|---|
| `Dataset-Rules/` | Original dataset workbook (read-only, SHA-256 pinned) and the participant packet |
| `data/processed/` | Cleaned CSVs: assets, events, production, readings, sites, solutions, HSE |
| `src/casequest/` | Cleaning, 39 integrity checks, metrics, option modeling, rollout roadmap, readiness signals |
| `tests/` | Automated tests for cleaning rules, dataset integrity, analysis and the recommendation |
| `docs/` | Phase write-ups, cleaning log, reconciliation checks, fact pack, external research, team plan |
| `prototype/` | Parvius, the operations console with the Parvis voice agent (single HTML file, `parvius.html`) |
| `web/` | Vercel hosting for the console plus the shared dispatch API (parts orders, engineer jobs) |
| `mobile/` | Expo app for the field engineer's phone, talks to the dispatch API |

Docs, in reading order: `phase-1-discovery`, `phase-2-data-audit`, `phase-3-fact-pack`, `phase-4-solution-selection`, `phase-5-product-design`, plus `cleaning-log`, `reconciliation`, `research-external`, `grader-reports` and `team-plan`.

## Prototype: Parvius

**Live:** <https://casequest-2026.vercel.app>

Parvius is the Lone Mesa operations console: `prototype/parvius.html`, a single self-contained HTML file. The engineer's phone app in `mobile/` and a small dispatch API in `web/` work alongside it.

### What it does

Every page is "as of" the 2025 day being replayed, using only readings received by that date. Every number is labelled **recorded** (solid outline) or **modeled** (dashed outline).

| Page | What it's for |
|---|---|
| **Map** | 3D map of the six sites: safety-hold cages, spare-shelf cubes and avoided-hours towers. The **inspector** on the right shows the field overview, a site (hold status, equipment, HSE approval workflow, open checks) or an asset (7-day early warning, 60-day vibration, planner decision). **Timeline lanes** along the bottom show each site's stops and overdue critical checks; drag to scrub through 2025. A six-beat **story mode** walks the pitch. |
| **Overview** | What's going on in plain English: sites on hold, machines down, what might break next, what to do first. |
| **Work** | Safety checks to verify, readiness flags to decide, and what's blocked behind a hold. |
| **Predicted failures** | The failure model's alerts for the replay day, on the Overview, the map's field overview, the asset inspector and the Work board: likely cause, chance of failure within 3 days, the readings behind it and which kits are on the shelf. As Manager, **Send engineer** orders any missing kit and books the engineer to arrive as it lands. The 3D map shows the parts truck and the engineer driving out and back; the phone app in `mobile/` gets the job live. |
| **Trends** (`#/site/S04`) | One site's 2025 trends by day, week or month: vibration per asset, downtime by stage, parts-wait, this month against last, any two periods side by side, causes and every stop. Open it from a site's inspector or by double-clicking a site on the map. |
| **Briefings** | Why this problem, business case (rollout sliders reproduce 666 h year one and 968 h steady state), safety and guardrails (with a self-test), plan and KPIs. |

**Roles and guardrails.** "Acting as" (HSE supervisor, Planner, Manager) enforces the gate rules:
- A hold has no override; only a verified closure lifts it.
- Only an HSE supervisor can sign a closure. The sign-off needs a name, a witness, a date no later than today, an evidence note and a field-verification confirmation.
- Only the planner stages a kit, with a logged reason, and never at a held site.
- Managers watch progress and run dispatch.
- Every action lands in an append-only, exportable decision log.

**Parvis** is the briefing agent, in the right-hand analysis column and the `Ctrl K` command bar. It answers from the data with a rules engine (no LLM or API key) and never lifts a hold or authorizes work. Whisper handles speech input and Kokoro provides an HD British male voice.

**Design.** The look follows the "Parvius Operations" Claude Design file and its Industry design system:
- Barlow Condensed headings over Barlow body text, with IBM Plex Mono labels.
- Square hairline frames with registration marks.
- Red means blocked or stopped, amber an early warning, and green cleared.

### Run it

The live site needs no setup. To run the console locally, serve it so the mic and voice models work (opening the file directly can block them):

```bash
cd prototype && python3 -m http.server 8000
```

Open <http://localhost:8000/parvius.html> in Chrome or Edge. Click **Download HD voices** in the `Ctrl K` bar once on good wifi before the demo.

Dispatch talks to the live API. Opened straight from disk, the console can't reach it. To run the console and the API together on a laptop:

```bash
cd web && npm install && npm run dev   # console + API with an in-memory store
```

Then open <http://localhost:3300/>. The engineer's phone app runs with Expo Go (`cd mobile && npm install && npx expo start --lan`); see `mobile/README.md`. More detail: `prototype/README.md` and `web/README.md`.

The Streamlit "Parts Readiness Console" described in `docs/phase-5-product-design.md` is designed but not yet in this repo.

## Rebuild the data and run the tests

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv run python -m casequest.build      # clean the raw workbook, run all checks, regenerate docs
uv run python -m casequest.factpack   # regenerate docs/phase-3-fact-pack.md
uv run pytest                         # run the test suite
```

The raw workbook is never modified. Cleaning rules are logged in `docs/cleaning-log.md`, and the build refuses to write if an integrity check fails.

## Team

Austin Nguyen, Aayan Khan, Nick Shahbazian, Sidra Shaikh, Wali Lambert. Roles and the presentation split are in `docs/team-plan.md`.

---

*University of Houston | CaseQuest 2026*
