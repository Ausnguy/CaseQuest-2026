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
| `prototype/` | Standalone 3D Gate Console with the Parvis voice agent (single HTML file) |

Docs, in reading order: `phase-1-discovery`, `phase-2-data-audit`, `phase-3-fact-pack`, `phase-4-solution-selection`, `phase-5-product-design`, plus `cleaning-log`, `reconciliation`, `research-external`, `grader-reports` and `team-plan`.

## Prototype: Gate Console and Parvis

`prototype/lone-mesa-gate-console.html` is a single self-contained interactive file:

- **3D site map** with HSE HOLD cages, spare-shelf cubes and avoided-hours towers
- **Roles** (Planner, Site HSE supervisor, Manager) enforcing the gate rules: no override on a hold, only a supervisor records verified closure, planners approve with a logged reason
- **2025 replay** using only readings received by the chosen date, with readiness flags
- **Rollout and business-case sliders** (reproduces 666 h year one and 968 h steady state)
- **Guardrail self-test** and an append-only, exportable decision log
- **Parvis**, a voice agent that briefs a plant manager, parts planner, HSE supervisor or executive from the data (rules engine, no LLM or API key). Whisper handles speech input and Kokoro provides an HD British male voice. It never lifts a hold or authorizes work.

Run it from a local server so the mic and voice models work (opening the file directly can block them):

```bash
cd prototype && python3 -m http.server 8000
```

Open <http://localhost:8000/lone-mesa-gate-console.html> in Chrome or Edge. Click **Prepare voices (~370 MB)** once on good wifi before the demo. More detail in `prototype/README.md`.

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
