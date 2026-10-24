# Slide Plan: 10 Slides in 5 Minutes

**Show format (7 minutes, then 3 minutes of Q&A):**
1. 1-minute video (problem + app overview)
2. 1-minute live app demo
3. **5 minutes of slides**

**Framing rule:** this is **ONE solution: the Critical Spare Parts Program**.
- The app (map, readiness console, field chat, HSE gate) is **how the program runs**. It is not a second recommendation.
- Never say "hybrid", "two options" or "also recommend".
- Sensors at Arroyo are only a *future expansion of the same program*, if it earns it.

The slides follow the **order of the judges' rubric sheet**.

> **Heads-up:** the rubric sheet differs from the packet PDF. The sheet makes HSE a **5-point bonus** and storytelling **15**. The packet says HSE is 15 and storytelling a 5-point bonus. We cover both fully, so either version scores.

| # | Rubric criterion (pts) | Slide title | What's on it | Speaker | Time |
|---:|---|---|---|---|---:|
| 1 | Business problem (15) | **"Machines wait for parts, and Arroyo waits most"** | 6,599 h of unplanned downtime and $5.6M of lost margin (2025). **24% of downtime is waiting for parts.** Priority site: **Arroyo**, with 30% of downtime and only 42% spare fill. 6 overdue severity-5 safety actions | Aayan | 0:30 |
| 2 | Data analysis (20) | **"Empty shelves predict waiting"** | Scatter: share of breakdowns that waited vs spare fill, 6 sites, **r = −0.995**. Small stage bar: repair 35%, parts 24%, dispatch 18%, detect 15%, restart 7% | Austin | 0:30 |
| 3 | Data analysis (20) | **"Every number is checked"** | Raw → cleaned: duplicates removed, IDs fixed, °F→°C, unknowns kept unknown. **39 automated checks**, 99 tests, independent audit. Limitations: synthetic data, daily snapshots, 6 sites (n=6) | Austin | 0:30 |
| 4 | Technology (20) | **"How the program runs: architecture"** | Diagram: field phone chat → ticket → operator console ← daily readings + parts data → **human approves** → storeroom. HSE gate sits in front of every site | Wali | 0:30 |
| 5 | Technology (20) | **"Who decides what"** | Three roles: technician reports, planner approves or rejects (logged), HSE supervisor unlocks sites. **The AI only drafts tickets and never authorizes work.** Phase 1 uses existing exports, with no new integration | Wali | 0:30 |
| 6 | Storytelling bonus (15) | **"From finding to fix"** | One line: *empty shelves → waiting → stock the right parts → safety first → 968 h/yr back*. Every number labeled OBSERVED or MODELED | Aayan | 0:25 |
| 7 | Implementation (10) | **"12-month rollout, safety first"** | Timeline: month 0–1 close safety actions ($33k) → month 1 **pilot at Canyon** → month 2 Cedar and Juniper → Arroyo after sign-off → Mesa and Prairie. Owners and training. **Expand / revise / stop** at month 6 and month 9 using KPIs: parts-wait per event, % waiting, overdue critical actions = 0 | Sidra | 0:35 |
| 8 | Recommendation and costs (10) | **"What it costs"** | Stacked bar: $168k program + $59.5k safety backlog = **$227.5k upfront, $19.5k/yr**. Staffing fits every site's hours. Benefit: **968 h/yr** (666 h in year 1) | Nick | 0:30 |
| 9 | Recommendation and costs (10) | **"What it makes"** | Running-total line: **payback month 8**, **+$1.98M over 3 years**, about 8× benefit/cost. Band: worst case month 16, best case month 6. Footnote: modeled margin, not cash | Nick | 0:35 |
| 10 | HSE bonus (5) + Presentation (10) | **"Safe by design, and our ask"** | Safeguards: no override of the HSE gate; corrosion/leak reports trigger "stop, make safe, call HSE"; the plan never shortens LOTO, repair or restart; every decision logged. **Ask: approve $227.5k to start the safety sprint and the Canyon pilot Monday** | Sidra → Aayan | 0:25 |
| | | | | **Total** | **5:00** |

## Lines to say, by slide
1. "Lone Mesa lost 6,600 hours last year. A quarter of it was machines **waiting for a part**."
2. "The emptier a site's shelf, the more often its machines wait. The pattern is almost perfect."
3. "We didn't trust the raw data. We cleaned it, wrote down every change, and 39 checks prove the numbers add up."
4. "Here's how it runs. A technician reports from the field, the planner decides on a PC, and the storeroom stocks it."
5. "People make every decision. The software only helps them see it."
6. "One finding, one fix: stock the right parts, safety first."
7. "We pilot where it's safe, prove it, then expand. If the KPIs don't move by month 9, we revise or stop."
8. "$227k upfront, and a fifth of it is safety work Lone Mesa owes anyway."
9. "It pays for itself in about 8 months. Even if everything goes wrong, it still pays back in 16."
10. "Nothing in this plan skips a safety step. Approve it, and the safety sprint starts Monday."

## Q&A (3 minutes)
Use the answers in `docs/financial-case.md` §6 and `docs/team-plan.md`. If asked "isn't the app a second recommendation?", answer: **"No. It's the operating system for the spare-parts program. We claim zero hours from it."**
