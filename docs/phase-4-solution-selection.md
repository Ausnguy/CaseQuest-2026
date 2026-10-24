# Phase 4: Solution Selection and Recommendation

**Date:** 2026-10-23
**Inputs:**
- [phase-3-fact-pack.md](phase-3-fact-pack.md): observed baseline and modeled strategies
- [research-external.md](research-external.md): OSHA, NIOSH, DOE, NASA, NIST, CISA and GAO evidence
- three **AI grader agents** (fresh Sonnet contexts, identical instructions, blind to our preference). This is internal decision support, **not** human judges; record in [grader-reports.md](grader-reports.md)

> **Like I'm 5:** Three judges each tasted all 8 medicines on their own, without knowing which one we liked. All three picked the same favorite.

## 1. Independent grader scores (out of 105)

| Strategy | Grader 1 | Grader 2 | Grader 3 | **Mean** | Rank |
|---|---:|---:|---:|---:|---:|
| **A. Spare parts (O4), all sites** | 88 | 84 | 88 | **86.7** | **1** |
| G. Hybrid: O4 + O1 on top-6 assets | 87 | 82 | 84 | 84.3 | 2 |
| B. Condition monitoring (O1) | 84 | 78 | 84 | 82.0 | 3 (tie) |
| F. Hybrid: O4 + O1 all assets | 85 | 79 | 82 | 82.0 | 3 (tie) |
| E. Hybrid: O4 + O3 | 83 | 77 | 80 | 80.0 | 5 |
| H. O1 + O3 | 74 | 73 | 74 | 73.7 | 6 |
| C. Work-order workflow (O3) | 72 | 65 | 72 | 69.7 | 7 |
| D. Refurbishment (O5) | 54 | 48 | 53 | 51.7 | 8 |

- **#1 pick:** A, from all three graders, each recommending a **gate-first, phased rollout**.
- **#2 pick:** G, G, and B (grader 3 had B and G tied at 84).
- **Confidence:** medium, from all three.

## 2. Why A wins (points all three graders raised)

1. **Best evidence-to-claim fit.**
   - At each site, the share of breakdowns that wait for parts ≈ 1 − spare-fill %. Arroyo is 56% vs 58%; Juniper is 10% vs 8%; r ≈ −0.99 across the 6 sites.
   - When parts are missing, the wait is long (about 16–18 h) whatever the cause.
   - O4 is the only option that cuts **parts-wait**, and it applies to every failure cause (O3 also covers all causes, but only detect and dispatch).
2. **Best economics, lowest delivery risk.**
   - $235 upfront per avoided hour, versus $304–$1,155 for the others.
   - 1 month to commission, no prerequisites, no site over its project-hour budget.
3. **Cleanest rule fit.**
   - One primary, no dependencies.
   - It only shortens *waiting for a box*. It never compresses detect, dispatch, repair or restart, so LOTO, gas monitoring and controlled restart are untouched.
4. **The HSE gate becomes the headline instead of an obstacle.**
   - Closing the 6 overdue severity-5 actions costs about **$33k and 48 person-hours**.
   - That unlocks the 76% of A's benefit that sits at Mesa, Arroyo and Prairie.

## 3. Why the hybrids lost points

- **Rule risk.** The ReadMe says *"Select one primary improvement and include any required supporting options."*
  - O4 doesn't require O1 or O3, and they don't require it.
  - All three graders said a literal judge would treat a hybrid as **two recommendations**.
- **No synergy in the model.** E = A + C exactly, and F = A + B exactly, because they touch different downtime stages. The hybrids are additive.
- **The monitoring half is slow and fully gated.**
  - O1 needs the data platform first: about 5 months to commission.
  - In G, every monitored asset sits at a blocked site.
  - NASA's RCM guide notes that a new RCM program typically **raises** cost for 2–3 years before saving (§3.5.3).
- **More build in 6 hours, more to explain in 7 minutes.**

## 4. Red flags graders found, and what we did

| Red flag | Action |
|---|---|
| Sensor backtest is "too clean" (≈100% detection, no false alarms vs Navy field rates of 0.76–0.92 detection and 0.08 false alarms) | Relabeled **feasibility, not proof** in the fact pack. It will never be presented as validating savings. |
| "Held-out" second half wasn't truly held out | Wording corrected |
| Lead time ignored the prerequisite chain | Fixed: O1 = 5 months, O3 = 3, O4 = 1 (tested) |
| Only steady-state benefit shown; ReadMe asks about first year | Added (`roadmap.py`): **A = 666 h in year 1** if closures are verified by month 3 (483–788 h for month 6 to month 1) |
| Uniform 60% parts-wait cut is generous at Cedar and Juniper, which already rarely wait | Present a range. Optionally show "core 4 sites" (849 h, $167.5k upfront) |
| HSE cost bundle hidden inside totals | Show separately: "HSE backlog, needed regardless" |
| $85/h extra-help rate is an internal rate | Labeled an assumption |
| A's biggest risk: judges see "just inventory" and cap Tech at about 14/20 | Prototype must be a real decision console (see options below) |

## 5. Decision (made by the team, 2026-10-23)

**Option 2: Critical spare parts (O4) as the single primary, a gate-first rollout, a sensor-aware parts-readiness feature in the app, and condition monitoring at Arroyo as a costed Phase 2.**

> **Like I'm 5:** We give the company **one** medicine: keep the right spare parts on the shelf so broken machines don't sit waiting. We fix the overdue safety problems **first**, because some sites aren't allowed to start until those are done. Our app also has a helper that notices when a machine starts to rattle and says "maybe get its parts ready". A person always decides. Later, if the first medicine works, Arroyo can try the fancier sensor medicine.

## 6. The recommendation

### What
- **O4, Critical spare parts program, at all 6 sites.**
  - Includes the inventory audit and annual replenishment, per the Solutions sheet.
  - No prerequisites.
  - It shortens only the **parts-wait** stage, for **every** failure cause.

### Rollout: gate first (`roadmap.gate_first_waves`)

| Month | Wave | Sites | Why |
|---|---|---|---|
| 0 | HSE closure sprint | Fund and track all 11 overdue actions; **sev-5 first** at Mesa, Arroyo, Prairie | ReadMe: open sev-5 actions block the site pilot until the site HSE supervisor verifies closure |
| 0 → 1 | Pilot | **Canyon (S05)** | Not blocked; mid-range spare fill (78%); 3 technicians, 180 project hours |
| 2 | Wave 2 | Cedar (S01), Juniper (S03) | Not blocked; lowest return. Review continuation at month 9 |
| after verification + 1 | Wave 3 | **Arroyo (S04)** | Largest prize: 387 h, 40% of parts-wait hours, 42% spare fill |
| + 1 more month | Wave 4 | Mesa (S02), Prairie (S06) | After verified closure |

### Benefit (MODELED, base fractions; not a promise)

| Measure | Value |
|---|---|
| Steady-state avoided unplanned downtime | **968 h/yr** (14.7% of 2025 unplanned hours). Low–high: 565–1,210 h |
| **Year 1** (depends on how fast closures are verified) | **666 h** if verified by month 3. Range **483 h** (month 6) to **788 h** (month 1) |
| Modeled avoided contribution margin, steady state | about $842k/yr (ReadMe contribution formula). A modeled margin, not cash. No repair-cost savings claimed |
| By site, steady state | Arroyo 387 · Mesa 196 · Prairie 149 · Canyon 117 · Cedar 66 · Juniper 53 h |

### Cost

| Line | Upfront | Annual |
|---|---:|---:|
| O4 × 6 sites | $168,000 | $18,000 |
| **HSE backlog: 11 open actions** (needed regardless of the recommendation) | $59,500 | $1,500 |
| … of which the **6 severity-5 actions that unlock the pilot** | $33,000 | $1,500 |
| **Total** | **$227,500** | **$19,500** |

- That is about $235 upfront per avoided hour (steady state).
- No fixed spending cap applies (ReadMe).

### Resources and training

Training effort follows the ReadMe: technicians × `training_hours_per_person`, once per site. It is counted in hours against each site's project hours.

| Site | Install 20 + HSE actions | Training | Total required | Available project hours | Headroom |
|---|---:|---:|---:|---:|---:|
| Cedar | 28 | 48 | 76 | 210 | 134 |
| Mesa | 44 | 60 | 104 | 170 | 66 |
| Juniper | 20 | 40 | 60 | 220 | 160 |
| **Arroyo** | 44 | 56 | 100 | 120 | 20 (only 2 technicians, so schedule carefully) |
| Canyon | 28 | 48 | 76 | 180 | 104 |
| Prairie | 44 | 54 | 98 | 165 | 67 |
| **Total** | 208 | 306 | 514 | 1,065 | 551 |

- No digital-training **fees** (O6) are charged for O4: O6 is required only for O1 or O3. If a reviewer wants them charged anyway, add $36,000 upfront and $7,200 a year (O6, $6,000 + $1,200 per site).
- Training **effort** is still counted (306 h in total, the base case). Every site fits its budget; Arroyo has 20 h of headroom, so its training goes after its HSE closures.
- *Assumption:* console setup for the planner and storekeeper is covered by O4's 20 install hours per site. Site HSE supervisors own the verified closures.
- Training is paid once. Phase 2 reuses Arroyo's 56 training hours, so its 214 h total and +94 h of help are unchanged.

### KPIs: 2025 baseline (OBSERVED), tracked monthly

| KPI | Arroyo | Mesa | Prairie | Canyon | Cedar | Juniper | Source of definition |
|---|---:|---:|---:|---:|---:|---:|---|
| Parts-wait hours per unplanned event | 9.48 | 5.83 | 4.51 | 4.24 | 2.30 | 2.21 | NASA RCM §14.3 (time to repair includes parts delivery) |
| Share of unplanned events that waited for parts | 56% | 38% | 29% | 22% | 12% | 10% | Our data (≈ 1 − spare fill) |
| Spare fill % | 42 | 65 | 70 | 78 | 86 | 92 | Assets |
| Overdue critical (sev-5) HSE actions | 2 | 2 | 2 | 0 | 0 | 0 | ReadMe "HSE measures" |

- **Targets.** The modeled base case cuts parts-wait hours 60% at live sites. We track progress against that; we don't guarantee it.
- **HSE target:** overdue critical actions = 0 before any blocked site goes live.
- **Also tracked:**
  - unplanned downtime hours
  - planner override rate on readiness flags (NIST AI RMF)
  - readiness-flag precision, reported as-is and not claimed in advance
  - emergency-maintenance share, target < 10% (DOE FEMP Table 3.1.1)

### App feature: sensor-aware parts readiness (decision support only)

**Scope boundary.** This is what keeps the ask to one primary.
- **In the ask (Phase 1):**
  - The parts console is the planner's working view of the **O4 program**: inventory audit, stock-out risk, pre-staging decisions and the HSE gate.
  - Readiness flags are computed from the **existing daily readings export**. The company already receives these snapshots centrally (`received_utc`), so this is a batch file, exactly like the prototype.
  - **No new integration, no historian connection and no automated alerts.**
  - *Assumption:* setting up the console is part of O4's program setup (20 install person-hours per site). It is not a Solutions-sheet option.
- **Not in the ask:**
  - Live integration with the ERP/CMMS and the sensor historian, plus automated alerting. That is **O2 "Data integration and alert platform"** ($40,000 upfront + $18,000/yr), and it sits in the costed Phase 2.
  - **Sensitivity:** if Lone Mesa wanted live integration in Phase 1, the ask would rise to **$267,500 upfront and $37,500/yr**, with no extra modeled hours.
- **The AI field-report chat is outside the ask.** It's a prototype concept: it doesn't change detect or dispatch time (so it isn't O3) and it claims zero hours. A production version needs live integration, which comes with Phase 2's O2 platform.
- **Not the O3 work-order workflow.** The planner's approve/reject step is part of O4's stocking program. It isn't the O3 work-order workflow, so the Dictionary's site-cleanup requirement ("required for workflow or monitoring") isn't triggered. **Sensitivity:** if a reviewer disagreed, site cleanup at all 6 sites would add $68,000 upfront.

**How flags work**
- **What triggers a flag:** any **valid, running** reading in the last 7 days above 1.3× the asset's normal vibration, or an operator "abnormal noise" note. Notes count whatever the sensor quality flag says that day, because they are human observations.
- **What the flag says:** pre-stage a bearing/seal kit.
- **Workload:** about 4 assets flagged per weekly snapshot across the fleet. The range is 0–14 in 2025.

**Guardrails**
- A planner approves, edits or rejects every flag, with a reason, and decisions are logged.
- A flag never authorizes work and never touches LOTO, permits or restart.
- Suspect and missing readings are never used as vibration evidence, and data gaps are shown.

**Claims.** No downtime reduction is claimed from this feature. In the case's own backtest the signal preceded every bearing and seal failure, but that data is synthetic: *feasibility, not proof*.

### Phase 2 (roadmap, costed, NOT part of the ask): condition monitoring at Arroyo

| | Value |
|---|---|
| Scope | O1 on A010, A011, A012, plus required O2 platform (which also brings live integration and alerting for the console), O6 training, Arroyo cleanup, Arroyo edge buffering (92.8% uptime) |
| Incremental benefit (modeled, steady state) | **+188 h/yr** (bearing and seal causes only) |
| Incremental cost | **+$133,990 upfront, +$35,300/yr** (incl. $7,990 assumed help at $85/h) |
| Time to commission | 5 months (O2 platform, then O1) |
| Resources | Arroyo needs 214 h vs 120 available: **+94 h of help** (assumed $85/h). O2's 60 install hours are charged to Arroyo, the only site using it, which is the conservative choice |
| Go/no-go at month 6 of Phase 1 | (1) Arroyo's sev-5 actions verified closed; (2) O4 live at Arroyo with parts-wait per event falling; (3) readiness-flag precision and planner override rate acceptable on real data; (4) staffing for the 94 h gap confirmed |

NASA's RCM guide notes that a new RCM program typically costs more for 2–3 years before saving (§3.5.3). Condition monitoring is a core RCM technology, so this is a gated Phase 2 and not part of the ask.

### Safety considerations
- O4 never compresses detect, dispatch, repair or restart. LOTO verification, gas monitoring, no lone work near tanks, and controlled restart are untouched (29 CFR 1910.147; NIOSH/OSHA 2016-108).
- **Protected repair time is never reduced.** The case model enforces this.
- **No safety claims.** We claim no incident or injury reduction (ReadMe forbids it), and no spill benefit, since net uncontained spill is already 0.

### Risks

| Risk | Mitigation |
|---|---|
| HSE verification slips | First-year range is already shown (483–788 h). The pilot and unblocked sites still deliver about 236 h/yr |
| Uniform 60% reduction is generous at Cedar/Juniper | Present the range; review those two at month 9 |
| Judges see "just inventory" | The app is a real decision console: risk scoring, review queue, HSE lock, readiness flags, architecture |
| Readiness flags over-trusted | Advisory only; overrides logged; precision measured on real data before any Phase 2 decision |
