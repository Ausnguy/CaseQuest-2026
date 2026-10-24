# Phase 6: Implementation, Adoption, Security and Field Safety

**Status:** Draft for slides 8 and 9. Not yet reviewed by the team.
**Scope rule:** One primary improvement, the critical spare-parts program (O4), gate-first. Engineer dispatch is a **supporting option**: it helps get the right people and parts to the job, and **no avoided hours are claimed for it**.

## 1. Rollout (slide 9)

Gate-first waves from `casequest.roadmap` (verification in month 3, one-month lead time per site):

| Live month | Wave | Sites | Why |
|---|---|---|---|
| 0 | HSE sprint | Mesa, Arroyo, Prairie | Close six severity-5 actions: $33k, 48 person-hours |
| 1 | Pilot | Canyon | Not blocked; 78% spare fill; 3 technicians |
| 2 | Wave 2 | Cedar, Juniper | Not blocked; lowest return, so review at month 9 |
| 4 | Wave 3 | Arroyo | Largest prize: 40% of parts-wait hours, 42% spare fill |
| 5 | Wave 4 | Mesa, Prairie | Staggered, each needs its own audit and stocking |

Year-one result: 666 hours if closures are verified by month 3. If verification slips to month 6, year one is 483 hours. Steady state is 968 hours a year (modeled).

## 2. Training and resources (slide 9)

The ReadMe defines training effort as technicians × training hours per person, once per site. Install and HSE hours come from phase 4, which uses the same table.

| Site | Training h | Install + HSE h | Total h | Available h | Headroom |
|---|---:|---:|---:|---:|---:|
| Cedar | 48 | 28 | 76 | 210 | 134 |
| Mesa | 60 | 44 | 104 | 170 | 66 |
| Juniper | 40 | 20 | 60 | 220 | 160 |
| Arroyo | 56 | 44 | 100 | 120 | 20 |
| Canyon | 48 | 28 | 76 | 180 | 104 |
| Prairie | 54 | 44 | 98 | 165 | 67 |
| **Total** | **306** | **208** | **514** | **1,065** | |

Training effort (306 hours in total) is the base case and is counted against each site's project hours. Digital-training fees (O6) are not charged, because O6 is required only for O1 or O3; if a reviewer wants them, add $36,000 upfront and $7,200 a year. Every site still fits its budget, but Arroyo has only 20 hours of headroom with two technicians, so schedule its training around the HSE work.

**Training format:** one hour per role on the console, plus a walkthrough of the phone app for engineers.

## 3. Adoption (slide 9)

- **Pilot as proof:** Canyon runs first, and its results decide the rest of the rollout.
- **Who does what:** planners review readiness flags within 24 hours; storekeepers pre-stage kits; site HSE supervisors record verified closures; engineers use the phone app for dispatched jobs; managers track KPIs.
- **Measure adoption:** planner override rate on readiness flags. A high override rate means the flags are not yet useful, so the team retrains or retunes.

## 4. KPIs (slide 9)

| KPI | Arroyo baseline (2025) | Definition source |
|---|---|---|
| Parts-wait hours per unplanned event | 9.48 | NASA RCM §14.3 |
| Share of events that waited for parts | 56% | Our data (≈ 1 − spare fill) |
| Spare fill | 42% | Assets sheet |
| Overdue severity-5 HSE actions | 2 (target 0 before go-live) | ReadMe, HSE measures |

Also tracked: unplanned downtime hours; planner override rate (NIST AI RMF); readiness-flag precision, reported as measured and not claimed in advance; emergency-maintenance share, target under 10% (DOE FEMP). The modeled base case cuts parts-wait hours 60% at live sites. We track progress against that and do not guarantee it.

## 5. Risks (slide 9)

- **Closures slip:** year one falls from 666 to 483 hours. Show this case on the slide.
- **Arroyo staffing:** two technicians and 20 hours of headroom. It goes last, after its training.
- **Overclaiming:** the sensor backtest is too clean on scenario data. Present flag precision as measured, not as proof.

## 6. Security and roles (slide 8)

| Role | Can | Cannot |
|---|---|---|
| Planner | Review flags; approve, edit or reject pre-staging with a reason | Verify HSE closures; lift a hold |
| Site HSE supervisor | Record verified closure for their own site (name, date, evidence) | Approve parts decisions; bypass a severity-5 action |
| Engineer (phone app) | Accept and close dispatched jobs; see the safety checklist | Change parts orders or HSE status |
| Manager / viewer | View everything; adjust scenario sliders; request field work | Change any safety record |

**Honest status:** the console's role picker is a demonstration. In production, company SSO assigns roles and the server enforces them. The prototype does not enforce roles server-side, so the slide must say so. The decision log is append-only and exportable, and every approval and closure records who did it and why.

**Responsible use:** the system is advisory. No flag, button or message authorizes maintenance, lock-out/tag-out, permits or restart. Every number is labeled OBSERVED or MODELED.

## 7. Field safety checklist (engineer phone app)

The ReadMe says detailed procedures must be defined by qualified site staff, and the dataset is not an operating instruction. So the engineer guide is a **checklist that points to the site procedure**, not a list of repair steps written by us.

Before any work:
1. Confirm the job is authorized and the site hold status is shown.
2. Confirm isolation and lock-out/tag-out are in place, following the site procedure.
3. Confirm the permit for the task, if the site requires one.
4. Wear the PPE the site procedure specifies for this task. OSHA oil and gas hazard guidance is the background reference.
5. Follow the repair steps in the site's own procedure for this asset type.
6. Restart only under the site's controlled restart procedure.

The guide never tells anyone to skip a step or bypass a control. If a step is missing from the site procedure, the engineer stops and calls the supervisor.

Sources: `Dataset-Rules/CaseQuest2026Dataset.xlsx` (ReadMe: Start here, Choose one improvement, HSE decision gate, HSE scope, Safety guidance); `docs/phase-4-solution-selection.md`; `docs/team-plan.md`.
