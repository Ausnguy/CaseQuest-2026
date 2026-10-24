# Team Plan

**Deadline:** Saturday Oct 24, 4:45 PM submission. Judging check-in 4:45; judging from 5:00 (MH 160).
**Format:** 10 slides or fewer, 7 minutes or less, **everyone speaks**, then Q&A on data, method and recommendation.

> **Like I'm 5:** Five friends put on one show. Each person gets a part they're good at, everyone gets a turn to talk, and everyone knows the whole story in case the judges ask them anything.

## Roles (by interest)

| Person | Interest | Build role (Sat AM) | Presentation part |
|---|---|---|---|
| **Aayan** | Everything | Integrator: final review of numbers, app and slides; owns the story | Opening hook and the ask (slides 1, 10). Q&A traffic controller |
| **Austin** | Data | Owns the analysis: verify every slide number against `docs/`, and run the build and tests | "What the data shows" (slides 2–3) |
| **Nick** | Product | Recommendation and costs: option comparison, cost table, resources | "Our recommendation and what it costs" (slides 4–5) |
| **Wali** | Full-stack | Streamlit prototype lead: app structure, deploy and run on the demo laptop | Live demo and architecture (slides 6–7) |
| **Sidra** | Product | HSE gate, rollout roadmap, training and KPIs; the employee-review workflow in the app | "Safe rollout, training and KPIs" (slides 8–9) |

## Presentation format (updated Oct 24)

**Superseded:** the old 10-slide skeleton is replaced by **`docs/presentation-plan.md`**. The new format is:
- 1-minute video
- about 1 minute of live demo
- **10 slides in 5 minutes, in judge-rubric order**
- 3 minutes of Q&A, separate from the 7 minutes

| Speaker | Slides |
|---|---|
| Aayan | 1, 5, 9 |
| Austin | 2–3 |
| Wali | 4 + the demo |
| Nick | 7–8 |
| Sidra | 6, 10 |

## Schedule

| When | What | Who |
|---|---|---|
| Fri night | Finish analysis, choose the strategy, freeze the numbers | Aayan, Austin, Nick |
| Fri night | Read `docs/research-external.md` and pick 2–3 citations each | Everyone |
| Sat 9:00–12:00 | Build the prototype | Wali (lead), Sidra (review and HSE screens), Austin (data hooks) |
| Sat 9:00–12:00 | Draft slides | Nick, Aayan |
| **Sat 12:00** | **Feature freeze.** Only bug fixes after this. | Everyone |
| Sat 1:00–2:00 | Meal; dry run #1 | Everyone |
| Sat 2:30–3:00 | Pitch workshop (at least one person required) | Nick and Sidra |
| Sat 3:00–4:30 | Dry runs #2–3; Q&A drills; backup screenshots of the app | Everyone |
| **Sat 4:45** | **Submit deck and prototype** | Aayan |

## Q&A prep: everyone must be able to answer
- Why this problem and not another? (Show the numbers.)
- How did you clean the data? (39 checks; nothing invented; unknowns stay unknown.)
- Are the savings real? (They're modeled using the case's own reduction fractions. First-year results will be lower.)
- What stops someone using this to skip safety? (The HSE gate is a hard block; humans approve every action.)
- What happens if a sensor is wrong or offline? (Alerts are advisory, and manual inspection routes remain.)
