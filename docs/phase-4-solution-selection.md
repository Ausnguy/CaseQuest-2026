# Phase 4: Solution Selection (decision pending)

**Date:** 2026-10-23
**Inputs:**
- [phase-3-fact-pack.md](phase-3-fact-pack.md): observed baseline and modeled strategies
- [research-external.md](research-external.md): OSHA, NIOSH, DOE, NASA, NIST, CISA and GAO evidence
- three independent graders (fresh Sonnet agents, identical instructions, blind to our preferences)

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
- **#2 pick:** G, G and B.
- **Confidence:** medium, from all three.

## 2. Why A wins (points all three graders raised)

1. **Best evidence-to-claim fit.**
   - At each site, the share of breakdowns that wait for parts ≈ 1 − spare-fill %. Arroyo is 56% vs 58%; Juniper is 10% vs 8%; r ≈ −0.99 across the 6 sites.
   - When parts are missing, the wait is long (about 16–18 h) whatever the cause.
   - O4 is the only option that helps **every** failure cause.
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
  - NASA notes that new predictive programs typically **raise** cost for 2–3 years before saving.
- **More build in 6 hours, more to explain in 7 minutes.**

## 4. Red flags graders found, and what we did

| Red flag | Action |
|---|---|
| Sensor backtest is "too clean" (≈100% detection, no false alarms vs Navy field rates of 0.76–0.92 detection and 0.08 false alarms) | Relabeled **feasibility, not proof** in the fact pack. It will never be presented as validating savings. |
| "Held-out" second half wasn't truly held out | Wording corrected |
| Lead time ignored the prerequisite chain | Fixed: O1 = 5 months, O3 = 3, O4 = 1 (tested) |
| Only steady-state benefit shown; ReadMe asks about first year | To add in the roadmap: **A ≈ 634–791 h in year 1**, depending on how fast the gate is verified |
| Uniform 60% parts-wait cut is generous at Cedar and Juniper, which already rarely wait | Present a range. Optionally show "core 4 sites" (849 h, $167.5k upfront) |
| HSE cost bundle hidden inside totals | Show separately: "HSE backlog, needed regardless" |
| $85/h extra-help rate is an internal rate | Labeled an assumption |
| A's biggest risk: judges see "just inventory" and cap Tech at about 14/20 | Prototype must be a real decision console (see options below) |

## 5. Decision needed

| Option | What we present | Pros | Cons |
|---|---|---|---|
| **1. A-Gated (pure)** | O4 at all sites. Gate first: close the sev-5 actions, pilot at Canyon, then Arroyo, Mesa and Prairie. Condition monitoring is a one-line "future" mention. | Unanimous grader #1; zero rule risk | Lowest Tech ceiling |
| **2. A-Gated + "sensor-aware parts readiness" (recommended)** | Same single primary (O4). The prototype uses the **existing** daily readings and operator notes as an *advisory* signal to pre-stage bearing and seal kits. O1 at Arroyo is shown as a **costed Phase 2 with a go/no-go gate**. No downtime benefit is claimed from sensors. | Keeps one primary; delivers your hybrid idea as a roadmap and app feature; lifts the Tech and Data story | Must word carefully so it isn't seen as a stealth second recommendation; backtest caveats must be stated |
| **3. G hybrid** | O4 + O1 on 6 assets as joint recommendations | Highest tech ceiling | All graders flagged the two-primary rule risk; more cost and build; all O1 assets are gated |
