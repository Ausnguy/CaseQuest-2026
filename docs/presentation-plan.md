# Presentation Plan: 7 minutes + 3 minutes Q&A

> **Like I'm 5:** First a 1-minute movie shows the problem and what our app does. Then we drive the real app for a minute. Then we flip through 10 picture-cards in 5 minutes, about 30 seconds each, in the same order the judges' score sheet lists things. That way the judges can tick boxes as we go.

## Format

| Segment | Time | Who |
|---|---:|---|
| Video: problem + app overview | 1:00 | (recorded) |
| Live app demo | about 1:00 | Wali drives; Aayan narrates if needed |
| **10 slides** | **5:00** | everyone (Aayan 3, Austin 2, Nick 2, Sidra 2, Wali 1 + the demo) |
| Q&A (separate from the 7 minutes) | 3:00 | everyone; Aayan routes questions |

## ⚠️ The judges' rubric differs from the PDF packet

| Criterion | PDF packet | **Judge rubric (attached image)** |
|---|---:|---:|
| Business problem and prioritization | 15 | 15 |
| Data analysis and evidence | 20 | 20 |
| Technology design / dashboard | 20 | 20 |
| **Data storytelling and credibility** | 5 (bonus) | **15 (counted in the base 100)** |
| Implementation and adoption | 10 | 10 |
| Recommendation, costs and resources | 10 | 10 |
| Presentation and clarity | 10 | 10 |
| **HSE, security and responsible use** | 15 | **5 (bonus)** |

**We follow the judge rubric for order and emphasis.** Storytelling now carries 15 points, so slide 5 is a full slide. HSE is a bonus, but it's still our differentiator and it's woven into slides 1, 4, 6 and 10. **Ask the organizers on Discord which rubric is final.**

The rubric's "what judges look for" phrases are quoted in each slide's **Rubric hook**, so the slide hits them word for word.

---

## The 10 slides (5:00 total, about 30 seconds each)

### Slide 1: Business problem and prioritization (15) · Aayan · 0:30
**Headline:** "Our machines don't wait for repairs. They wait for parts, and Arroyo waits the most."

**Visual:** three stat tiles (downtime / money / safety), then Arroyo highlighted.
- **Downtime:** 6,599 h of unplanned downtime in 2025. **24% (1,613 h) was spent waiting for parts.**
- **Financial:** $5.6M in lost contribution margin. **Arroyo alone accounts for $2.0M, 30% of all downtime and 40% of all parts-wait hours.**
- **Safety:** 6 overdue severity-5 HSE actions. Arroyo, Mesa and Prairie are locked out of any pilot until they're closed.

**Say:** "We prioritized one issue, parts waiting, and one site, Arroyo, using downtime, money and safety evidence together."

**Rubric hook:** *"Identify one priority site, asset or issue using downtime, financial and safety evidence."*

### Slide 2: Data analysis and evidence, part 1: clean and validated (20) · Austin · 0:30
**Headline:** "We cleaned 6 messy exports, changed nothing we couldn't prove, and checked every formula."

**Visual:** a before/after row-count table and a "39/39 checks pass" badge.
- **Cleaning:**
  - removed 6,594 duplicate readings, 2 duplicate events and 36 duplicate HSE rows
  - fixed 8 scrambled IDs
  - converted 4 °F temperatures
  - rebuilt 4 missing durations and 3 missing potentials using the case's own formulas
- **Validation:** 39 automated checks, 99 tests and an AI-agent skeptical audit (4 rounds). One command reproduces everything.
- **Limitations stated:**
  - the data is synthetic
  - readings are daily snapshots
  - 339 missing readings were left blank
  - 14 parts invoices are unknown, not $0
  - the site comparison is n = 6

**Rubric hook:** *"Clean and validate records, explain limitations and show accurate, reproducible calculations."*

### Slide 3: Data analysis and evidence, part 2: the key finding (20) · Austin · 0:30
**Headline:** "The emptier the shelf, the more often a breakdown waits for parts."

**Visual:** **the story chart.** A scatter of the 6 sites, with spare-fill % on the x-axis and the share of breakdowns that waited for parts on the y-axis, along a line. Arroyo sits top-left: 42% fill, 56% waited. Juniper sits bottom-right: 92% fill, 10% waited.
- **Correlation:** r = −0.995. A waiting breakdown loses about 16–18 h whatever the cause.
- **Only spare parts touch this stage.** It's the only option that cuts parts-wait, and it helps every failure cause.

**Say:** "This is why we chose spare parts and not sensors first."

### Slide 4: Technology design and integration (20) · Wali · 0:30
**Headline:** "Simple architecture: the company's existing data in, decisions by people out."

**Visual:** the architecture diagram, left to right:
1. Existing exports: readings, work orders, HSE register
2. Cleaning and 39 checks
3. Rules engine: stock-out risk, readiness flags, HSE gate, payback
4. Streamlit console: site map, parts console, HSE gate
5. **Human decisions:** the planner approves pre-staging, and the HSE supervisor verifies closures
6. Append-only audit log

The AI field-report chat is **not** on this diagram. It's an optional prototype concept, outside the ask; see the note under slide 10.

**Point out:** the demo they just saw maps onto each box. In the ask there is no new integration. Live integration is in Phase 2.

**Rubric hook:** *"Explain a practical architecture and how supplied data supports useful outputs, employee decisions and human review."*

### Slide 5: Data storytelling and credibility (15) · Aayan · 0:35
**Headline:** "Every number traces back: finding, then assumption, then recommendation, then benefit."

**Visual:** a 4-box chain, with each box labeled **OBSERVED** or **MODELED**:
1. **Finding (OBSERVED):** 24% of downtime is waiting for parts; empty shelves predict waits.
2. **Assumption (MODELED, from the case's Solutions sheet):** the parts program cuts parts-wait 60% (range 35–75%).
3. **Recommendation:** spare parts at all 6 sites, safety first.
4. **Benefit (MODELED):** 968 h/yr avoided (565–1,210); 666 h in year 1.

**Small "what we did NOT claim" box:**
- no injury or incident prevention
- no repair-cost savings
- no hours from sensors or AI
- the sensor backtest is "feasibility, not proof"

**Rubric hook:** *"An especially clear, traceable story connecting findings, assumptions and the recommendation."*

### Slide 6: Implementation and adoption (10) · Sidra · 0:30
**Headline:** "A 12-month roadmap: safety first, pilot, then expand only if it works."

**Visual:** a timeline with owners.

| Month | Step | Owner |
|---|---|---|
| 0–3 | Close the 11 overdue HSE actions, severity-5 first | Site HSE supervisors |
| 1 | **Pilot at Canyon**: inventory audit, stock critical spares | Maintenance planner + storekeeper |
| 2 | Cedar and Juniper go live | Site planners |
| 4 | **Arroyo goes live** once verified | Arroyo planner (2 technicians, 44 of 120 h used) |
| 5 | Mesa and Prairie go live once verified | Site planners |
| 6 | Phase 2 (Arroyo sensors) go/no-go | Ops manager |
| 9 | Review whether Cedar and Juniper continue | Ops manager |

- **Training:** console training for planners and storekeepers (within the 20 install hours per site; our assumption). HSE supervisors get the verification step.
- **Pilot measures** (our proposal):
  - **Leading KPI: Canyon spare fill %**, measured weekly. Baseline 78%. Across sites, the share of breakdowns that wait ≈ 1 − fill, so a fill of about 90% points to roughly 10% waiting. This is approximate: it applies the six-site pattern to one site.
  - **Outcome KPI: parts-wait hours per breakdown**, baseline 4.24. Treat it as directional only. Canyon has about 4 breakdowns a month and only about 1 in 5 waits, so a 3-month average is too noisy to decide on.

| Decision | Condition |
|---|---|
| **Expand** (month 3) | Canyon fill ≥ 90% and no safety-control bypass |
| **Revise** | Fill < 90% at month 3, or waits not trending down by month 6: re-check stocking lists |
| **Stop** | Any safety-control bypass, or no improvement in fill or waits by month 6 |

**Rubric hook:** *"Twelve-month roadmap with owners, training, a pilot and measures for expanding, revising or stopping."*

### Slide 7: Recommendation, costs and resources (10) · Nick · 0:30
**Headline:** "One improvement: $227.5k upfront, $19.5k a year, 968 hours of downtime avoided a year."

**Visual:** a cost stack plus a resources table.
- **One improvement:** the Critical Spare Parts Program (O4) at 6 sites.
- **Costs:**

| Item | Upfront | Per year |
|---|---:|---:|
| Parts program | $168k | $18k |
| **Supporting activity:** closing the HSE backlog | $59.5k | $1.5k |
| **Total** | **$227.5k** | **$19.5k** |

- **Staffing:** fits every site's available project hours. **Training:** included in O4's 20 install hours per site (our assumption).
- **Annual downtime benefit:** 968 h (565–1,210). Year 1: 666 h.

**Rubric hook:** *"Recommend one improvement. Estimate upfront/annual costs, supporting activities, staffing/training and annual downtime benefit."*

### Slide 8: Recommendation, costs and resources (cont.): what it earns · Nick · 0:30
**Headline:** "It pays for itself in about 8 months."

**Visual:** a cumulative **modeled margin** line from month 0 to 36. It dips to −$148k, **crosses zero at month 8**, and reaches **+$1.98M by year 3**. Shade a band from month 6 (best case) to month 16 (everything goes wrong).
- **Year 1:** +$332k net. **NPV:** about $1.66M (10%, 3 years). **Benefit ÷ cost:** about 8×.
- **Stress tested:** low effect + slow safety sign-off + oil at about $50 still pays back by month 16.
- **Footnote:** MODELED contribution margin (the case formula), not cash. Case prices ($63–73) are in line with EIA's ~$65 2025 WTI estimate (via Rigzone; check EIA's own series before the final deck).

**Say:** "The biggest lever is closing the safety actions fast, which is why safety comes first."

### Slide 9: Presentation and clarity: why it's worth doing · Aayan · 0:20
**Headline:** "Three reasons to say yes."
1. **It targets the biggest fixable delay:** parts waits, which happen at every site and with every failure cause.
2. **Cheap and fast:** 1-month lead, no prerequisites, pays back in about 8 months.
3. **Safe by design:** safety locks first; people make every decision.

**The ask:** approve $227.5k to start the safety sprint and the Canyon pilot next month.

**Rubric hook:** *"Explain the recommendation and evidence clearly … defend assumptions in Q&A."*

### Slide 10: Bonus, HSE, security and responsible use (5) · Sidra · 0:25
**Headline:** "It never trades safety for speed."
- **Hard HSE gate:** no site starts while a severity-5 action is open. **There is no override button**, and only the HSE supervisor can verify a closure.
- **Speeds up waiting, never work:** lockout/tagout, gas monitoring and controlled restart are untouched (29 CFR 1910.147; NIOSH/OSHA 2016-108).
- **Responsible AI:** sensor readiness flags **only advise**. A planner approves or rejects each one, and overrides are logged. (NIST AI RMF; CISA AI-in-OT.)
- **Security:**
  - role-based access, with SSO in production
  - append-only audit log
  - the app never writes to source data
  - no API keys in code
  - offline-safe: if data fails to load, every site shows HOLD

**Rubric hook:** *"Identifies HSE/security concerns and proposes practical safeguards for responsible use."*

**Total: 4:50, with 10 seconds of buffer.**

> **Note on the AI field-report chat.** If it gets built, show it only as an **optional prototype concept**, captioned *"prototype concept, not part of the $227.5k ask"*.
> - It is **not** the O3 work-order workflow: it doesn't change detect or dispatch time, and it claims **zero** hours.
> - A production version (phone-to-operator queue, automatic HSE routing) needs live integration, so it belongs with Phase 2's data platform.
> - If asked, the safety backstop is: hazard words → "Stop, make safe, call HSE".

---

## Video (1:00) outline: script owner Aayan, edit owner Wali

| Time | Content |
|---|---|
| 0:00–0:15 | **Problem:** "At Lone Mesa, a broken pump often sits idle not because of the repair, but because the part isn't on the shelf." Show 6,599 h, 24% waiting, the Arroyo map marker turning red |
| 0:15–0:45 | **What the app does**, quick cuts: site map with issue boxes → parts console with readiness flags → planner approves → HSE gate locked until verified → business case. *Optional last 5 seconds, only if built:* field-report chat, captioned "prototype concept, not in the ask" |
| 0:45–1:00 | **Payoff:** "Fewer waits, safety first, people in control." Show payback at month 8 |

**Rule:** the video gives a high-level overview. Don't repeat its numbers in detail on the slides; the slides prove them.

## Live demo (about 1:00), Wali
1. **Site map:** Arroyo red. Click it to show the issue box.
2. **Console** (Arroyo, 2025-10-15): A012 flagged. Approve the pre-stage with a reason; the log updates.
3. **HSE gate:** as a Planner, try to unlock, and it can't be done. Switch to Supervisor, verify both actions, and Arroyo turns ELIGIBLE.
4. **Business case:** move the verification month from 3 to 6, and year 1 drops from 666 h to 483 h.

The AI chat is only shown if it's working by the 12:00 freeze. Otherwise skip it.

## Q&A (3:00): who takes what
| Topic | Lead |
|---|---|
| Data, cleaning, limitations | Austin |
| Costs, payback, oil price | Nick |
| App, architecture, security | Wali |
| HSE gate, roadmap, training | Sidra |
| "Why not sensors / hybrid?", overall story | Aayan |

Rehearse these answers (more in `docs/team-plan.md` and `docs/financial-case.md`):
- **"Is the $842k real?"** It's modeled margin from the case formula, not cash. No repair savings are claimed.
- **"Why not condition monitoring?"** It only covers bearing and seal failures, takes 5 months to switch on, and is fully gated. It's costed as Phase 2 with a go/no-go.
- **"What if safety closure is slow?"** Payback moves from month 8 to month 10. The unblocked sites still deliver.
- **"Is the sensor result real?"** It's synthetic and too clean, so we call it feasibility, not proof, and claim zero hours from it.
