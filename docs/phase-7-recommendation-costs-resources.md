# Phase 7: Recommendation, Costs and Resources

**Status:** Draft for slides 4 and 5. Not yet reviewed by the team.
**Rubric:** Recommendation, costs & resources, 10 points. The ReadMe asks for upfront and annual costs of **one** recommendation "including prerequisites, training and open HSE actions in scope," annual avoided unplanned downtime hours with assumptions, resources, and any extra help with its assumed cost.
**Labels:** OBSERVED = what happened in 2025. MODELED = estimate from the Solutions sheet's reduction fractions. Not a promise.

## 1. The recommendation (slide 4)

**Problem.** Unplanned breakdowns: 313 events, 6,599 hours, about $5.6M modeled lost contribution in 2025. Bearing wear and seal leaks cause 58% of the hours, and repair is the largest stage (35%).

**Lever.** Waiting for parts is the largest part we can cut quickly: 1,613 hours (24%), present in about 30% of events at an average of 17 hours, across every failure cause. Arroyo holds 40% of it, with 42% spare fill.

**One primary improvement: a critical spare-parts program (O4) at all six sites, rolled out gate-first.**

| Element | Role | In the ask? | Hours claimed |
|---|---|---|---|
| Critical spare-parts program (O4), inventory audit and replenishment included | **Primary** | Yes | 968 h/yr steady state |
| Close the 6 severity-5 HSE actions at Mesa, Arroyo, Prairie | Required supporting action (HSE decision gate) | Yes | None. HSE benefits are unquantified |
| Parts-readiness console with planner review | How staff run O4 | Yes (inside O4's install hours) | None |
| Engineer dispatch (web + phone app) | Supporting tool: gets the right engineer and the parts to the job together | Yes, as support | **None** |
| Condition monitoring at Arroyo (O1 + O2) | Costed Phase 2 | No | Not in the ask |

**What it does not do:** it does not shorten repair, detect, dispatch or restart, so isolation, gas monitoring, lock-out and controlled restart are untouched. It does not address electrical, process or unknown causes beyond their parts-wait share.

**Why this one.** Only O4 cuts parts-wait, it applies to every cause, and it has no technology prerequisite and a one-month lead time. Cost is about $235 upfront per avoided hour, against $304 to $1,155 for the other options.

## 2. Costs (slide 5)

| Line | Upfront | Annual |
|---|---:|---:|
| Critical spares (O4) × 6 sites, $28,000 + $3,000/yr each | $168,000 | $18,000 |
| HSE backlog, 11 open actions (needed regardless of the recommendation) | $59,500 | $1,500 |
| of which the 6 severity-5 actions that unlock the pilot | $33,000 | $1,500 |
| Training effort (306 person-hours, see section 3) | in project hours | in project hours |
| Extra help | $0 in base case | $0 |
| **Total ask** | **$227,500** | **$19,500** |

**Prerequisites.** O4 has none (Solutions sheet). Digital training (O6) is required only for O1 or O3, so its fees are not charged in the base case. **Training effort is the base case in hours** (technicians × training hours per person, once per site, 306 in total) and is charged against each site's project hours, as the ReadMe's resource and training rows require. Phase 4 uses the same figures.

**Sensitivities (not in the ask):**
- Charge O6 digital-training fees anyway: +$36,000 upfront, +$7,200/yr ($6,000 + $1,200 per site), with no extra modeled hours.
- Live ERP/historian integration in Phase 1 (O2): $267,500 upfront, $37,500/yr, no extra modeled hours.
- Site cleanup at all six sites, if a reviewer treats the planner review step as the O3 workflow: +$68,000 upfront.

## 3. Resources

Required hours = 20 install + open HSE action hours (8 each) + training. Available hours come from the Assets sheet.

| Site | Install | HSE | Training | Total | Available | Headroom |
|---|---:|---:|---:|---:|---:|---:|
| Cedar | 20 | 8 | 48 | 76 | 210 | 134 |
| Mesa | 20 | 24 | 60 | 104 | 170 | 66 |
| Juniper | 20 | 0 | 40 | 60 | 220 | 160 |
| Arroyo | 20 | 24 | 56 | 100 | 120 | 20 |
| Canyon | 20 | 8 | 48 | 76 | 180 | 104 |
| Prairie | 20 | 24 | 54 | 98 | 165 | 67 |
| **Total** | 120 | 88 | 306 | **514** | 1,065 | 551 |

Every site fits its project-hour budget. **Arroyo is the tight one**: two technicians and 20 hours of headroom, so its training goes after its HSE closures. **Extra help** is assumed only as a contingency: if Arroyo's 100 hours had to be covered by outside help at the internal $85/h assumption, the worst case is $8,500. Engineer dispatch uses existing technicians, with no cost or benefit claimed.

## 4. Benefit and assumptions (MODELED)

- **Annual avoided unplanned downtime:** 968 hours at full implementation (14.7% of the 6,599 hours), range 565 to 1,210 (35% to 75% parts-wait reduction).
- **Assumptions:** the base 60% parts-wait reduction applies to all unplanned events at live sites; stage hours are original × (1 − reduction); protected repair time is untouched; one-month lead time per site; benefit begins the month after a site goes live.
- **Margin:** about $842k a year, valued at about $870 per avoided hour using the ReadMe contribution formula. A modeled margin, not cash. No repair-cost savings are claimed (14 of 385 work orders have pending parts invoices, which stay unknown, not zero, and historical maintenance is not automatically avoided).
- **First year is lower than steady state:** 666 hours if closures are verified by month 3 (range 483 at month 6 to 788 at month 1; low-to-high reduction case 388 to 832).

| Site | Steady-state h/yr | Modeled margin | Upfront (O4 + site HSE) | Annual | Payback at steady state |
|---|---:|---:|---:|---:|---:|
| Arroyo | 387 | $336,530 | $44,500 | $3,500 | 1.6 months |
| Mesa | 196 | $170,459 | $41,500 | $3,500 | 3.0 months |
| Prairie | 149 | $129,490 | $47,500 | $3,500 | 4.5 months |
| Canyon | 117 | $101,725 | $34,000 | $3,000 | 4.1 months |
| Cedar | 66 | $57,644 | $32,000 | $3,000 | 7.0 months |
| Juniper | 53 | $46,152 | $28,000 | $3,000 | 7.8 months |
| **Total** | **968** | **$842,000** | **$227,500** | **$19,500** | |

Cedar and Juniper already rarely wait for parts, so their benefit is the most generous assumption. Review both at month 9.

## 5. Year one (gate-first rollout, MODELED)

| Scenario | Year-1 hours | Year-1 net after all costs | Payback month |
|---|---:|---:|---:|
| Base, closures verified month 3 | 666 | $337k | 8 |
| Closures verified month 1 | 788 | $441k | 6 |
| Closures verified month 6 | 483 | $180k | 10 |
| Low case (35%), month 3 | 388 | $96k | 10 |
| High case (75%), month 3 | 832 | $482k | 7 |

Each month the safety gate stays shut costs about 61 avoided hours (about $53k of modeled margin). Net = year-1 modeled margin minus $227.5k upfront and run costs, with costs timed to each site's go-live.

## 6. Phase 2, not in the ask: condition monitoring at Arroyo

From phase 4: +188 h/yr (bearing and seal only), +$133,990 upfront and +$35,300/yr including assumed outside help, 5 months to commission. Spares at Arroyo gives 387 h for $28,000 in one month, so monitoring waits until the spares program proves out.

## 7. Slide copy

**Slide 4: Our recommendation (Nick, 45 s)**
- Problem: breakdowns cost 6,599 hours and about $5.6M in 2025.
- Lever: 24% of that is machines waiting for a part, across every cause. Arroyo is 40% of it.
- One solution: a critical spare-parts program at all six sites, released site by site after safety closures are verified.
- Support, not extra claims: safety closures, a planner review console, and engineer dispatch. No hours are claimed for them.

**Slide 5: Costs, resources, avoided hours (Nick, 40 s)**
- Ask: $227.5k upfront, $19.5k a year, of which $59.5k is a safety backlog needed regardless.
- Avoids about 968 hours a year (565 to 1,210). Year one is 666 hours.
- Fits every site's project hours (514 of 1,065). Arroyo is tight, so it goes last.
- Modeled from the case's own rates, not cash.

## 8. Likely questions

- **Why not fix repairs, the biggest stage?** No option except refurbishment (O5) shortens repair. It costs $42k per asset, applies to pumps only, and adds six planned outage hours per treated asset in year one. Our blind graders ranked it last.
- **Is $842k real?** It is modeled margin from the ReadMe formula at the base reduction. We show low and high cases and a year-one figure well below steady state.
- **Why no payback guarantee?** The ReadMe does not require ROI or payback. We show them for context, labeled MODELED.
- **What if safety closures slip?** Year one falls to 483 hours at month 6. Unblocked sites still deliver about 236 hours a year.

Sources: `Dataset-Rules/CaseQuest2026Dataset.xlsx` (ReadMe, Solutions, HSE); `data/processed/*.csv`; `docs/phase-4-solution-selection.md`; `docs/phase-6-implementation-adoption.md` (on `feature/implementation-adoption`).
