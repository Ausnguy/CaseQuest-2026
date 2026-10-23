# Phase 5: Product Design. "Parts Readiness Console" (Streamlit)

**Status:** design approved for build on Saturday morning. Feature freeze at **12:00**.

> **Like I'm 5:** Before building the toy, we draw the picture of it. This page is the picture: what buttons it has, who is allowed to press which button, and what it must never do.

## 1. Who uses it and what for

| Role | Job in the app | Can | Cannot |
|---|---|---|---|
| **Maintenance / parts planner** | Decide what to stock and pre-stage at each site | Review readiness flags: approve, edit or reject, with a reason. View stock-out risk and the rollout plan | Verify HSE closures; lift a site's hold |
| **Site HSE supervisor** | Own the HSE gate for their site | Record **verified closure** of an open HSE action (name, date, evidence note) | Approve parts decisions; bypass an open sev-5 action |
| **Manager / viewer** | Track the business case and KPIs | View everything; adjust scenario sliders | Change any record |

Roles are picked from a dropdown in the demo. **Production would use company SSO**, which is noted on the architecture slide.

## 2. Screens (one Streamlit page each)

1. **Overview: the problem**
   - KPI tiles:
     - 2025 unplanned downtime **6,599 h**
     - modeled lost contribution **$5.6M**
     - **24%** of downtime spent waiting for parts
     - **6** overdue critical HSE actions
   - Chart: downtime by stage × site.
   - Chart: **share of breakdowns that waited for parts vs. spare fill %**, with the six site dots on a line (r = −0.995). *This is the story chart.*
2. **Parts readiness console: the employee workflow** (the core of the demo)
   - **Controls:** site picker, plus an "as of" date slider that replays 2025 using only data received by that date.
   - **Stock-out risk table** (site × asset type × cause), all from history:
     - events
     - share that waited for parts
     - average wait when waiting
     - risk rank
   - **Readiness flags** (`signals.readiness_flags`): assets with a vibration above 1.3× normal or an "abnormal noise" note in the last 7 days.
     - Each flag shows the evidence: readings, values vs normal, and a data-gap warning.
     - Planner action: **Approve pre-stage / Edit / Reject**, with a required reason.
   - **Decision log** for the current site.
3. **HSE gate: hold and authorization**
   - A status card per site: **HOLD** (red) or **ELIGIBLE** (green), with its open actions listed.
   - **Verified closure form**, Site HSE supervisor role only. It needs the action ID, the supervisor's name, a closure date of today or earlier, and an evidence note.
   - The site turns **ELIGIBLE** only when **all** its open sev-5 actions are verified.
   - **No override button exists.**
   - Banner: *"Recording closure here does not perform the work. The supervisor verifies in the field per site procedure."*
4. **Rollout and business case**
   - Sliders:
     - month HSE closure is verified (1–6)
     - reduction case (low / base / high)
     - pilot site (unblocked sites only)
   - Wave timeline, then year-1 vs steady-state hours: base **666 h** in year 1 and **968 h** at steady state.
   - Cost table, with the HSE backlog shown as its own line.
   - Phase 2 Arroyo card with its go/no-go criteria.
   - Every number is labeled **OBSERVED** or **MODELED**.
5. **KPIs**
   - The 2025 baseline by site (from `metrics.kpi_baselines`), the target direction, and the definition source.
6. **How it works**
   - The architecture diagram and the workflow diagram (§4), drawn with `st.graphviz_chart` from DOT text, so no extra dependency.
   - A link to the cleaning log and the reconciliation checks.

## 3. Rules the app must enforce (acceptance criteria)

| # | Rule | How to test |
|---|---|---|
| R1 | A site with any sev-5 action not yet verified as closed shows HOLD, and nothing in the app can switch it to ELIGIBLE | Unit test on the gate function; try to approve as a Planner |
| R2 | Only the Site HSE supervisor role can record a verified closure, and only for their chosen site's actions | Role test |
| R3 | A closure needs a name, a date no later than today, and an evidence note | Form validation test |
| R4 | Readiness flags use **only received** readings and ignore Suspect and Missing readings | Already tested in `tests/test_recommendation.py` |
| R5 | Every approve, edit, reject or verification is appended to the log with time, role, name and reason. **The log is never edited** | Log test |
| R6 | The app never writes to the raw workbook or the processed CSVs. Decisions go to a separate append-only file | File-hash test |
| R7 | If the data fails to load or checks fail, the app shows an error and **every site defaults to HOLD** (fails closed) | Simulated failure test |
| R8 | Every number on screen is labeled OBSERVED or MODELED, and modeled numbers show their assumption | Visual review |
| R9 | No flag or button authorizes maintenance work, LOTO, permits or restart | Copy review and a banner |

## 4. Architecture and workflow

**Prototype architecture** (what we built):

```
CaseQuest2026Dataset.xlsx (raw, read-only, SHA-256 pinned)
   └─ casequest.build: clean (logged rules) → 39 integrity checks → refuse if any fail
        └─ data/processed/*.csv
             └─ domain modules: metrics · options (Solutions rules) · roadmap · signals (readiness)
                  └─ Streamlit app (6 pages, role picker)
                       └─ data/app_state/decisions.jsonl (append-only audit log, git-ignored)
```

**Production architecture** (what Lone Mesa would run; on the slide, not built):
- **Inputs:** the ERP/CMMS inventory and work orders, the sensor historian, and site edge buffers (for Phase 2).
- **Pipeline:** the same cleaning and checks run nightly.
- **App:** the same rules engine, with SSO roles.
- **Alerts** go into the existing change-management process (CISA/NSA AI-in-OT guidance: passive recommendations, human decides).

**Employee workflow:**
1. A reading or note arrives.
2. A readiness flag appears.
3. The planner reviews it: approve, edit or reject.
4. The storekeeper pre-stages the kit.
5. *(Separate, unchanged)* if the machine fails or work is planned, the normal work order runs with LOTO, permits and controlled restart.

**HSE gate workflow:**
1. An open sev-5 action holds the site.
2. The field work is done.
3. The Site HSE supervisor records a verified closure.
4. When all sev-5 actions at the site are verified, the site becomes ELIGIBLE.
5. The site's wave goes live.

## 5. Build plan (Saturday 9:00–12:00)

| Who | Task | Done when |
|---|---|---|
| **Wali** (lead) | App skeleton: `app/Home.py` plus pages, data loading via `casequest`, role picker, decision-log module | App runs with `uv run streamlit run app/Home.py`; R5, R6 and R7 pass |
| **Sidra** | HSE gate page plus closure form; R1–R3 tests; banner copy | Gate tests pass; a Planner cannot verify |
| **Austin** | Overview charts and the KPI page; check every number against `docs/` | Numbers match the fact pack exactly |
| **Nick** | Rollout and business-case page (sliders → `roadmap` and `options`); Phase 2 card | Year 1 shows 666 h at month 3; costs match Phase 4 |
| **Aayan** | Readiness console page; architecture diagrams; end-to-end demo script; final review | 90-second demo runs cleanly twice |

**Rule:** all business logic stays in `src/casequest/` (already tested). Pages only display it and collect input.

## 6. Demo script (about 75 seconds, Wali)

1. **Overview:** "Here's the story chart: empty shelves mean waiting."
2. **Console:** Arroyo, date 2025-10-15. Show the flags on A012; approve a pre-stage with a reason; the log updates.
3. **HSE gate:** switch to Planner and try to lift Arroyo's hold. It can't be done. Switch to Supervisor and verify both sev-5 actions. Arroyo turns ELIGIBLE.
4. **Business case:** slide the verification month from 3 to 6, and year 1 drops from 666 h to 483 h. "That's why we fix safety first."

## 7. Open questions
- Hosting for judges: a local laptop is enough. Optionally use Streamlit Community Cloud from the public repo. That's a deploy decision for Saturday, and needs the team's OK because it publishes the app.
- Backup: if the live demo fails, use screenshots of each step (taken by 3:30 PM).
