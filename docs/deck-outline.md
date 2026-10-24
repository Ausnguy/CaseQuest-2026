# Deck outline: 10 slides, 6:45, five speakers

**Status:** Draft for the team to edit. Numbers come from `docs/phase-3-fact-pack.md`, `phase-4`, `phase-6` and `phase-7`. Labels: OBSERVED = 2025 data; MODELED = estimate from the Solutions sheet's rates, not a promise.
**Rules to hit:** at most 10 slides, at most 7 minutes, every member speaks and can answer questions on data, method and recommendation, one primary recommendation, prototype submitted with the deck.

## Open items before this deck is final

1. **Slide 7 needs a drawn workflow and architecture visual.** The ReadMe requires one. A text sketch is below; someone has to draw it.
2. **Name:** the deck, the repo and the console must use one name (Parvis or Parvius).
3. **Priority wording:** say "breakdowns are the problem, parts waiting is the lever" on every slide that names the priority. Parvis's own "problem to fix first" line should match.
4. **HSE measures:** the ReadMe lists repeated hazard observations and spilled minus recovered volume. Slide 8 should carry them (net uncontained spill is 0).
5. **Correction:** an earlier draft said repair costs are incomplete in nearly every work order. That is wrong: 14 of 385 work orders have pending parts invoices. Fixed in phase 7 and in Parvis's risk answer on this branch.

## Timing and speaker split

| # | Slide | Speaker | Time | Rubric points |
|---:|---|---|---:|---|
| 1 | The answer | Aayan | 0:30 | Problem 15 |
| 2 | Where downtime comes from | Austin | 0:45 | Problem 15, Data 20 |
| 3 | What we checked | Austin | 0:40 | Data 20, Bonus 5 |
| 4 | Our recommendation | Nick | 0:45 | Costs and resources 10 |
| 5 | Costs, resources, avoided hours | Nick | 0:40 | Costs and resources 10 |
| 6 | Live demo | Wali | 1:15 | Dashboard 20 |
| 7 | Workflow and architecture | Wali | 0:30 | Dashboard 20 |
| 8 | HSE, security and responsible use | Sidra | 0:45 | HSE 15 |
| 9 | Roadmap, training, KPIs | Sidra | 0:35 | Implementation 10 |
| 10 | The ask | Aayan | 0:20 | Presentation 10 |
| | **Total** | | **6:45** | 15 s buffer |

Pace: about 130 words a minute. The notes below are sized to the time.

---

## Slide 1: Lone Mesa lost 6,599 hours to breakdowns in 2025. One fix avoids about 15% of it. (Aayan, 0:30)

**On the slide:** one big number (6,599 h, about $5.6M modeled) and the recommendation in one line: *a critical spare-parts program at all six sites, released site by site after safety closures are verified.* Team names.

**Say:** "Lone Mesa lost 6,599 hours to unplanned breakdowns last year, about 5.6 million dollars in modeled lost contribution. We looked at every kind of loss, ranked them, and recommend one fix: a critical spare-parts program at all six sites, released site by site once the safety gate is cleared. It avoids about 968 hours a year, roughly 15 percent of the loss, for 227 thousand dollars upfront. Everything you'll see is labeled observed or modeled."

**Transition:** "Austin will show where the hours go."

## Slide 2: Breakdowns drive the loss, and waiting for parts is the largest piece we can cut quickly (Austin, 0:45)

**On the slide:** stacked bars of downtime by stage for each site; a small cause table (bearing wear 41%, seal leak 17%, electrical 15%, process 15%, unknown 12%); the shelf-versus-waiting scatter.

**Say:** "Of 6,599 hours, bearing wear and seal leaks cause 58 percent, and repair is the largest stage at 35 percent. Waiting for a part is second: 1,613 hours, 24 percent. It shows up in about 30 percent of breakdowns, 17 hours each, and across every cause, which is why one fix reaches all of them. It is concentrated: Arroyo holds 40 percent of it, with the emptiest shelf at 42 percent. Across the six sites, the emptier the shelf, the more breakdowns wait. Six sites is a small sample, so we call it a strong pattern, not a law."

**If asked "why not repairs":** see Q&A.

## Slide 3: We cleaned the data without inventing anything (Austin, 0:40)

**On the slide:** a before and after: readings 13,164 → 6,570 rows; five catches; "39 of 39 integrity checks pass"; a small early-warning panel.

**Catches to name (pick three):** 6,594 duplicate sensor rows removed after verifying each was identical; 161 legacy tags (LEG-nnn) mapped to the right asset; 339 missing readings left missing, with no guessing; 58 suspect readings kept and flagged; 14 pending parts invoices kept as unknown, not zero; temperatures in Fahrenheit converted; capacities with units fixed.

**Say:** "The export was intentionally dirty. We removed 6,594 identical duplicate readings, mapped 161 legacy tags, and left 339 missing readings missing rather than guess. Pending invoices stay unknown, not zero. All 39 integrity checks pass, and the raw file is untouched. On early warning: vibration rises about two days before bearing and seal failures, and not before electrical or process failures. The backtest is cleaner than real fleets would be, so we call it feasibility, not proof, and we claim no savings from it."

## Slide 4: One recommendation: a critical spare-parts program, gate first (Nick, 0:45)

**On the slide:** the table of primary and supports (below), and "what it does not do."

| Element | Role | Hours claimed |
|---|---|---:|
| Critical spare-parts program (O4) | **Primary** | 968 h/yr |
| Close the 6 severity-5 HSE actions | Required support (decision gate) | none |
| Planner review console and readiness flags | How staff run it | none |
| Engineer dispatch | Support: right person and parts together | none |
| Condition monitoring at Arroyo | Costed Phase 2, not in the ask | none |

**Say:** "Our one recommendation is a critical spare-parts program at all six sites. It has no technology prerequisite, a one-month lead time, and cuts waiting for every cause. Around it, three supports, none of which we claim hours for. First, closing six overdue severity-5 safety actions, because the rules block a site's pilot until a supervisor verifies them. Second, a review console so planners decide on every flag. Third, engineer dispatch so the right person arrives when the parts do. Monitoring waits for Phase 2. It does not shorten repair or touch any isolation or restart step."

## Slide 5: $227.5k upfront avoids about 968 hours a year, and every site's hours fit (Nick, 0:40)

**On the slide:** cost table; hours-per-site bar (514 of 1,065 hours); benefit range.

| Line | Upfront | Annual |
|---|---:|---:|
| Spares, 6 sites | $168,000 | $18,000 |
| HSE backlog (needed regardless) | $59,500 | $1,500 |
| **Total** | **$227,500** | **$19,500** |

**Say:** "The ask is 227,500 dollars upfront and 19,500 a year, of which 59,500 is a safety backlog the company needs regardless; closing the six that gate the pilot costs 33 thousand and 48 hours. That avoids about 968 hours a year, range 565 to 1,210, and 666 in year one. Training follows the rules' formula: 306 hours, and every site fits its project budget, 514 of 1,065 hours in total. These are modeled from the case's own rates, not promised cash, and year one is lower than steady state. In the rules' contribution formula that is about 842 thousand dollars of margin a year at the base case."

## Slide 6: Live demo: a safety gate that lifts only on a verified closure (Wali, 1:15)

**On the slide:** the console, or a recorded fallback. Demo script below.

1. **Overview (10 s):** "Three sites are on safety hold and 24 percent of the prize is unlocked."
2. **Click Arroyo (10 s):** hold cage, 42% shelf, 387-hour tower.
3. **Role: Site HSE supervisor (15 s):** record a verified closure with name, date and evidence. The cage drops and the tower lights up. Show that a Planner cannot do this.
4. **Role: Planner (15 s):** open a flag at a cleared site; approve a pre-stage with a reason. Show that approve is disabled at a held site.
5. **Rollout slider (10 s):** closures at month 3 gives 666 hours; month 6 gives 483.
6. **Optional (10 s):** one question to Parvis, such as "what is blocking the sites?"

**Say:** narrate as you click; keep to the six steps. **Fallback:** a 60-second screen recording and screenshots.

## Slide 7: How the workflow and the system fit together (Wali, 0:30)

**On the slide:** one diagram (to be drawn). Sketch:

- **Workflow:** daily readings and events → cleaned and checked → readiness flag (vibration above 1.3× normal or an operator noise note) → planner approves, edits or rejects with a reason → HSE gate (site must be eligible) → stock the kit → engineer dispatched when parts arrive → work done under the site's own procedure.
- **Architecture:** batch exports → nightly clean and 39 checks → console (roles, gate, replay) → dispatch API → engineer phone app. Phase 2 adds the data platform (O2) for live integration.

**Say:** "A flag appears from the daily readings, a planner decides, the safety gate has to be open, the kit is stocked, and the engineer is sent when the parts arrive. No step authorizes work, isolation, permits or restart; those stay with the site's own procedures. Today it runs on batch exports, so there is no new integration in the ask."

## Slide 8: Safety comes first: a hard gate, separate roles, and advice only (Sidra, 0:45)

**On the slide:** the role matrix, the gate, the field checklist, and "what we do not claim."

| Role | Can | Cannot |
|---|---|---|
| Planner | Review flags; approve, edit or reject with a reason | Verify closures; lift a hold |
| Site HSE supervisor | Record verified closure for their site | Approve parts decisions |
| Engineer | Take and close dispatched jobs; see the safety checklist | Change orders or HSE status |
| Manager | View everything; adjust scenarios | Change safety records |

**Say:** "Safety is the gate, not an afterthought. Mesa, Arroyo and Prairie each carry two overdue critical actions, gas monitoring readiness and energy isolation. Nothing is stocked there until a site HSE supervisor verifies closure, and there is no override. Roles are separated so planners cannot verify and managers cannot edit safety records. To be straight about the prototype: the role picker is a demonstration, and production would use company single sign-on with server-side enforcement. For field work, the engineer sees a checklist that points to the site's own procedure: confirm isolation, the permit and the required protective equipment, then follow that procedure. We do not write repair steps. We claim no injury or incident reduction; the data has no exposure figures to support one."

**Measures to show:** overdue critical actions (6), verified closures, repeated hazard observations, spilled minus recovered volume (0 net uncontained).

## Slide 9: A 12-month rollout: pilot, expand, then the biggest prize after safety closure (Sidra, 0:35)

**On the slide:** the wave timeline, a training and hours table, and KPIs.

| Live month | Wave | Sites |
|---|---|---|
| 0 | Safety sprint | Mesa, Arroyo, Prairie |
| 1 | Pilot | Canyon |
| 2 | Expand | Cedar, Juniper |
| 4 | Biggest prize | Arroyo |
| 5 | Remaining | Mesa, Prairie |

**Say:** "Month zero closes the safety actions. Canyon pilots first, because it is cleared and mid-range. Cedar and Juniper follow, then Arroyo once its closures are verified, then Mesa and Prairie. Training follows the rules' formula, 306 hours in total, and every site fits its budget; Arroyo has the least headroom, 20 hours, so it goes last. We measure parts-wait hours per event, share of breakdowns that waited, spare fill, overdue critical actions at zero before go-live, and planner override rate. If closures slip to month six, year one falls from 666 to 483 hours."

## Slide 10: The ask (Aayan, 0:20)

**On the slide:** three decisions and the number.

1. Approve $227.5k upfront and $19.5k a year.
2. Name a site HSE supervisor at Mesa, Arroyo and Prairie to verify the six critical closures.
3. Start the Canyon pilot, and review at month six before any Phase 2.

**Say:** "Three decisions: approve 227,500 dollars, name the supervisors who verify the six safety closures, and start at Canyon. Every month the safety gate stays shut costs about 61 hours. Thank you. We're ready for questions."

---

## Q&A cheat sheet (everyone should be able to answer all of these)

- **Why not fix repairs, the biggest stage?** Only refurbishment (O5) shortens repair. It costs $42k per asset, applies to pumps only, and adds six planned outage hours per treated asset in year one. Our blind graders ranked it last. Spares removes the part of a breakdown we can change in a month.
- **Is the $842k real?** It is modeled margin using the rules' formula at the base reduction. We show low and high cases (565 to 1,210 hours) and a smaller year-one figure.
- **Your correlation is six points.** Yes. We call it a strong pattern, not a law. The parts-wait share is also similar across causes, which supports the "fixes every cause" claim.
- **How reliable is the early-warning flag?** The backtest is cleaner than real fleets, so it is feasibility, not proof. It only covers bearing and seal failures, and we claim no savings from it.
- **What if safety closures slip?** Year one falls to 483 hours at month six. Unblocked sites still deliver about 236 hours a year.
- **Why not condition monitoring?** At Arroyo it costs about $134k more, needs five months, and avoids about 188 hours, against 387 hours for $28k with spares. It is a gated Phase 2.
- **Does engineer dispatch add to your savings?** No. We claim no hours for it.
- **Is the security real?** The roles are a design, and the prototype does not enforce them server-side. Production would use company sign-on.
- **What did you assume on training?** The rules' formula: technicians × hours per person, once per site, 306 hours in total, charged to project hours. The paid training option (O6) is not required for spares; charging it anyway adds $36k upfront and $7.2k a year.
- **Why do Cedar and Juniper look weak?** They already rarely wait for parts, so our 60 percent assumption is generous there. We review both at month nine.
- **Can Parvis approve anything?** No. It briefs and recommends only, and never lifts a hold or authorizes work.
- **What data problems did you find?** Duplicates, legacy tags, missing and suspect readings, Fahrenheit values, pending invoices. Each is logged in the cleaning log.

## Delivery checklist

- Everyone speaks, and everyone studies all the slides, not only their own.
- At least one member attends the 2:30 pitch workshop.
- Demo laptop: voices prepared, microphone allowed, fallback video ready.
- Submit the deck and the prototype together before 4:45 PM; confirm the method on Discord.
