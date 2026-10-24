# CaseQuest 2026: Team Handoff

**Last updated:** Sat Oct 24, 2026 (early morning)
**Deadline:** Sat Oct 24, **4:45 PM** submission (deck ≤ 10 slides + prototype). Judging check-in 4:45 in MH 160; 7 minutes per team; **everyone speaks**.

> **Like I'm 5:** A pretend oil company's machines keep breaking, and they sit broken for a long time waiting for spare parts. We're the doctors. Our one medicine: **keep the right spare parts on the shelf**. We fix the overdue safety problems **first**. And we build a little app so workers can use the plan.

---

## 1. Where we are

| Phase | Status | Where |
|---|---|---|
| 1. Discovery | Done | `docs/phase-1-discovery.md` |
| 2. Data cleaning and audit | Done, merged to `main` (4 skeptical audit rounds) | `docs/phase-2-data-audit.md`, `docs/cleaning-log.md`, `docs/reconciliation.md` |
| 3. Analysis | Done, merged | `docs/phase-3-fact-pack.md`, `docs/research-external.md` |
| 4. Recommendation | **Decided**, merged | `docs/phase-4-solution-selection.md`, `docs/grader-reports.md` |
| 5. App design | Spec done, merged | `docs/phase-5-product-design.md` |
| **6. Build the Streamlit app** | **NOT STARTED: Saturday 9:00–12:00** | §5 below |
| 7. Test | Not started | §5 |
| 8. Slides and rehearsal | Not started: Saturday afternoon | `docs/team-plan.md` |

All code lives in `src/casequest/` and is tested: 99 tests, 39 data checks.

## 2. The recommendation (memorize this)

**Critical spare parts program (option O4) at all 6 sites, as our ONE recommendation, rolled out "safety first".**

1. **Safety sprint first.** Close the 6 overdue severity-5 HSE actions at Mesa, Arroyo and Prairie ($33k, 48 person-hours). Those sites are **not allowed** to start until a site HSE supervisor verifies closure.
2. **Pilot at Canyon (S05).**
3. **Then Cedar and Juniper.**
4. **Then Arroyo, once verified.** It is the biggest win.
5. **Then Mesa and Prairie.**

| Number | Value | Type |
|---|---|---|
| 2025 unplanned downtime | 6,599 h across 313 events | OBSERVED |
| Lost contribution margin | $5.6M | OBSERVED events × the ReadMe formula |
| Share of downtime spent waiting for parts | 24% | OBSERVED |
| Share of breakdowns that waited for parts ≈ 1 − spare-fill % | r = −0.995 across 6 sites (Arroyo 56% vs 42% fill) | OBSERVED, **the story chart** |
| Avoided downtime, steady state | **968 h/yr** (range 565–1,210) | MODELED |
| Avoided downtime, **year 1** | **666 h** if safety is verified by month 3 (483–788) | MODELED |
| Upfront / annual cost | **$227,500 / $19,500**. $59,500 of the upfront is the HSE backlog, shown separately | From Solutions + HSE sheets |
| Staffing | Fits every site's available hours | Assets sheet |

**Sensor-aware "parts readiness" feature (app only).**
- It reads the daily sensor file the company already has.
- It flags about 4 machines a week (range 0–14) where vibration is above 1.3× normal or an operator heard abnormal noise, and suggests pre-staging a bearing/seal kit.
- **A planner approves or rejects every flag.**
- It never authorizes work.
- **We claim NO hours from it.**

**Phase 2 (roadmap only, NOT in the ask): condition monitoring at Arroyo**
- +188 h/yr for **+$133,990 upfront and +$35,300/yr**.
- 5 months to switch on; needs +94 h of help.
- A go/no-go decision at month 6.

### Money (details in `docs/financial-case.md`, all MODELED)
- **Payback: month 8.** Year-1 net about **+$332k**. 3-year net about **+$1.98M**. Benefit ÷ cost about 8×.
- **Worst case** (low effect + slow safety sign-off + oil margin −$15/bbl): it still pays back by **month 16**.
- **The biggest lever is how fast the safety actions are closed.**
- **Real-world check:** case oil prices ($63–73) are in line with EIA's ~$65/bbl 2025 WTI estimate (via Rigzone; confirm in EIA's series).

### New features agreed (details in `docs/decisions-log.md` #10 and the Phase 5 design §8)
- **Site map** with an issue box per site: must-have.
- **AI field-report chat**, phone to operator PC: an **optional prototype concept, NOT in the ask and NOT on the architecture slide**. Timeboxed 9–11, with a form fallback. Hazard words trigger a "Stop, make safe, call HSE" backstop. The AI only drafts tickets. Production would need Phase 2's data platform.

## 3. Things we must NEVER say (the judges will check)

- ❌ "Our sensors predict failures with 100% accuracy." The backtest is synthetic data: *feasibility, not proof*.
- ❌ "This prevents injuries or incidents." The ReadMe forbids injury/incident claims.
- ❌ "Guaranteed savings," "ROI," or "the AI decides." Benefits are MODELED using the case's own reduction fractions. Humans decide everything.
- ❌ "Independent judges picked this." Our graders were **AI agents**, for internal use only.
- ✅ Always label numbers **OBSERVED** (2025 data) or **MODELED** (an estimate).

## 4. How to run things

One-time setup, after installing [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/Ausnguy/CaseQuest-2026 && cd CaseQuest-2026 && uv sync
```

Run every test (should say 99 passed):
```bash
uv run pytest
```

Rebuild the clean data (should say 39/39):
```bash
uv run python -m casequest.build
```

Regenerate the fact pack:
```bash
uv run python -m casequest.factpack
```

- Clean CSVs for Excel or slides are in `data/processed/`. **Never edit them by hand**; they're regenerated.
- The original workbook `Dataset-Rules/CaseQuest2026Dataset.xlsx` is read-only. The build refuses to run if it changes.

## 5. Saturday build plan (9:00–12:00, feature freeze at 12:00)

The full spec is `docs/phase-5-product-design.md`. Build in `app/`, and run with `uv run streamlit run app/Home.py`. **Rule: the logic already exists in `src/casequest/`. Pages only display it and collect clicks.**

| Who | Build | Uses | Done when |
|---|---|---|---|
| **Wali** (lead) | App skeleton, data loading, role picker (Planner / HSE supervisor / Viewer), append-only decision log at `data/app_state/decisions.jsonl` (add it to `.gitignore`) | `casequest.clean.clean_all`, `casequest.validate.run_checks` | App runs. If data fails to load, **every site shows HOLD** |
| **Sidra** | HSE gate page: HOLD/ELIGIBLE per site; a closure form only the HSE supervisor role can submit (name, date ≤ today, evidence note); **no override button** | `data.sites["pilot_blocked"]`, `data.hse` | A planner cannot lift a hold (write a test) |
| **Austin** | Overview page (KPI tiles + the parts-wait vs spare-fill chart) and KPI page | `casequest.metrics.summarize`, `site_context`, `kpi_baselines` | Numbers match `docs/phase-3-fact-pack.md` exactly |
| **Nick** | Business-case page: sliders for verification month (1–6) and low/base/high; costs table; Phase 2 card | `casequest.options.model_plan`, `casequest.roadmap.gate_first_waves`, `first_year` | Shows 666 h at month 3 and 483 h at month 6; costs match Phase 4 |
| **Site map** (Austin or Wali, ~1 h) and **AI chat** (one owner, 9–11, timeboxed) | See Phase 5 design §8 | `metrics.site_context`, `signals.readiness_flags`, Claude Haiku 5.5 | Map colors match the gate; hazard words always route to HSE (tested) |
| **Aayan** | Readiness console (pick site and date; flags; approve/edit/reject with a reason; log), "How it works" diagrams (`st.graphviz_chart`), demo script, final review | `casequest.signals.readiness_flags` | Demo (Arroyo, 2025-10-15, A012 flagged) runs twice cleanly |

**Demo script, about 75 seconds:**
1. Overview chart: "empty shelves mean waiting."
2. Console: approve a pre-stage for A012 at Arroyo, with a reason. The log updates.
3. HSE gate: as a Planner, try to lift Arroyo's hold, and it can't be done. Switch to Supervisor, verify both sev-5 actions, and Arroyo turns ELIGIBLE.
4. Business case: slide verification from month 3 to 6. Year 1 drops from 666 h to 483 h. "That's why safety comes first."

**Backup:** take screenshots of every demo step by 3:30 PM in case the live demo fails.

## 6. Saturday afternoon: the presentation

**Full plan: `docs/presentation-plan.md`.**

| Segment | Time |
|---|---:|
| Video | 1:00 |
| Live demo | ~1:00 |
| **10 slides, in judge-rubric order** | **5:00** |
| Q&A (separate) | 3:00 |

| Speaker | Slides |
|---|---|
| Aayan | 1, 5, 9 |
| Austin | 2–3 |
| Wali | 4 + the demo |
| Nick | 7–8 |
| Sidra | 6, 10 |

- ⚠️ **The judge rubric differs from the PDF.** Storytelling is 15 points and HSE is a 5-point bonus. Confirm on Discord which one is final.
- At least one person must attend the 2:30 pitch workshop.
- Do 2 or more full timed dry runs.
- Take backup screenshots of the demo by 3:30.

## 7. Team process rules we agreed

- **Nothing goes to `main` without a skeptical review.** Use a PR, and have someone who didn't write it check the numbers against `docs/`.
- Work on branches, one per person or feature. Merge by PR.
- If a number on a slide doesn't match `docs/phase-4-solution-selection.md` or the fact pack, the docs win. Ask Austin.

## 8. Best citations for slides (details in `docs/research-external.md`)

- **GAO-03-887:** missing parts blocked 58% of Navy work orders. Use it as an analogy for why spares matter.
- **29 CFR 1910.147 (LOTO)** and **NIOSH/OSHA 2016-108:** safety steps our plan never shortens.
- **NIST AI RMF / CISA AI-in-OT guidance:** humans approve alerts, and overrides are logged.
- **NASA RCM guide §3.5.3:** new RCM/monitoring programs cost more for 2–3 years. That's why sensors are Phase 2.
