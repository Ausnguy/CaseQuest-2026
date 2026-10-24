# Financial Case: Cost, Benefit, Payback

**Model:** `src/casequest/finance.py`, built on `options.model_plan` and `roadmap.gate_first_waves`. Tested in `tests/test_finance.py`.

> **Like I'm 5:** We spend about $228k to stock the shelves and fix the safety problems. Every month after that, machines spend less time broken, so the company keeps more of the oil money. Around **month 8** the money saved has paid back the money spent, and after that it's profit.

## Ground rules: where every number comes from

| Input | Source | Why |
|---|---|---|
| Costs (O4, HSE actions) | **Case Solutions and HSE sheets** | ReadMe: "do not infer market pricing" |
| Hours avoided | Case Solutions base fractions, applied with the ReadMe rules | Required method |
| Dollar benefit | **Modeled avoided contribution margin** = avoided oil × (1 − recoverable fraction) × (price − variable cost), using the ReadMe formula | It's margin, not cash. No repair-cost savings are claimed |
| Timing | Gate-first waves (`roadmap.py`) | Assumption, shown |
| Discount rate | 10%/yr, **our assumption** | Conservative. The US government's 2025 rate for 3-year analyses is 3.7% nominal (OMB A-94 Appendix C) |
| Real-world checks | EIA, DOE/PNNL, GAO, NASA, OMB, Anthropic pricing | Sanity checks only, never inputs |

The ReadMe says ROI and payback are **not required**. We show them because judges will ask. We label them MODELED, and we lead with hours avoided.

## 1. What it costs

| | Upfront | Per year |
|---|---:|---:|
| Spare-parts program (O4) × 6 sites | $168,000 | $18,000 |
| HSE backlog: 11 overdue actions (needed regardless) | $59,500 | $1,500 |
| … of which the 6 severity-5 actions that unlock the pilot | $33,000 | $1,500 |
| **Total ask** | **$227,500** | **$19,500** |

**Optional add-ons, NOT in the ask:**

| Add-on | Upfront | Per year | Note |
|---|---:|---:|---|
| Live data integration and alerts (O2) | +$40,000 | +$18,000 | Comes with Phase 2 |
| Site data cleanup, if a reviewer counts the console as a "workflow" | +$68,000 | — | |
| **AI field-report chat** (Claude Haiku 5.5: $0.10 / $0.50 per million input/output tokens) | — | **about $2–25** in AI usage | Assumes 200–2,000 reports a month at about 5k input and 800 output tokens each. Hosting and development aren't priced in the case, so they are labeled as an assumption |

## 2. What it's worth (MODELED)

| | Year 1 | Year 2 | Year 3 |
|---|---:|---:|---:|
| Avoided downtime (hours) | 666 | 968 | 968 |
| Avoided contribution margin | $574,050 | $842,354 | $842,354 |
| Costs | $242,250 | $19,500 | $19,500 |
| **Net** | **+$331,800** | **+$822,854** | **+$822,854** |
| **Cumulative** | +$331,800 | +$1,154,654 | **+$1,977,508** |

| Headline | Base case |
|---|---|
| **Payback** | **Month 8** |
| 3-year net benefit | **about $1.98M** |
| NPV, 3 years at 10% | about $1.66M |
| Benefit ÷ cost, 3 years | about 8× |

**Monthly path, base case:**
- Months 1–5 are negative, the investment phase. Spending is: month 1 the HSE sprint and the Canyon pilot; month 2 Cedar and Juniper; month 4 Arroyo; month 5 Mesa and Prairie.
- After month 5 the plan earns about +$68,600 a month.
- The cumulative total turns positive in **month 8**.

## 3. Stress tests: what if we're wrong?

| Scenario | Payback | Year-1 net | 3-yr cumulative | Benefit ÷ cost |
|---|---:|---:|---:|---:|
| **Base** (safety verified by month 3, base fractions) | **month 8** | +$332k | +$1.98M | 8.0× |
| Fast safety sign-off (month 1) | month 6 | +$442k | +$2.09M | 8.4× |
| Slow safety sign-off (month 6) | month 10 | +$167k | +$1.81M | 7.5× |
| Low effect (the case's "low" fractions) | month 10 | +$93k | +$1.04M | 4.7× |
| High effect | month 7 | +$475k | +$2.54M | 10.0× |
| Oil margin −$15/bbl, so WTI around $50 | month 10 | +$126k | +$1.17M | 5.1× |
| Low effect + slow sign-off | month 13 | −$2k | +$0.94M | 4.4× |
| **Everything goes wrong** (low effect + slow sign-off + margin −$15) | **month 16** | −$88k | +$0.50M | 2.8× |
| Safety never verified, so only 3 sites go live (HSE work still paid) | month 13 | ≈ $0 | +$0.33M | 2.9× |

**The takeaway:**
- Every scenario pays back within about 16 months.
- **The biggest lever is how fast the safety actions are closed.** That's why safety comes first in the plan.

## 4. Phase 2 (sensors at Arroyo), for the roadmap slide only

| | Value |
|---|---|
| Extra cost | +$133,990 upfront, +$35,300/yr |
| Extra benefit (MODELED) | +188 h/yr, about +$188k/yr of contribution |
| Earliest start | Go/no-go decision at month 6, then 5 months to commission, so live around month 12 |
| Payback of the increment | about **10–11 months after it goes live** ($133,990 ÷ ($188k − $35k)/yr) |
| Caveat | NASA's RCM guide expects new programs to cost more for 2–3 years. Our numbers are case-modeled, so we keep Phase 2 gated |

## 5. Real-world sanity checks (sources)

| Check | Real-world figure | Our case | Verdict |
|---|---|---|---|
| Oil price | EIA estimated **WTI averaged about $65.40/bbl in 2025** (Jan 2026 STEO, as reported by Rigzone) | Case prices $63–73, average $67 | The case is realistic. Our −$15 stress is roughly $50 WTI |
| Payback of maintenance-management investments | DOE/PNNL FEMP O&M Guide cites a 1994 survey of 558 companies using a maintenance management system: **14.5-month average payback**, 20.1% less downtime. It's an old survey, so we use it as context only | Base payback 8 months; worst 16 | Same ballpark |
| Missing parts really do stall work | GAO-03-887: **58% of Navy work orders** couldn't be completed because parts weren't on board | 24% of our downtime is parts wait | Supports the problem choice (as an analogy) |
| Discount rate | OMB A-94 Appendix C, 2025: **3.7% nominal for 3 years** (US government) | We use 10% | We're more conservative |
| New monitoring programs cost before they save | NASA RCM Guide §3.5.3: about 2–3 years | Sensors are kept in Phase 2 | Consistent |
| AI chat cost | Anthropic API pricing for Claude Haiku 5.5: $0.10 / $0.50 per million tokens (input / output) | About $2–25/yr | Negligible |

**Source links:**
- [EIA forecast coverage (Rigzone, Jan 2026)](https://www.rigzone.com/news/where_will_the_wti_oil_price_land_in_2026_and_2027-19-jan-2026-182794-article/)
- [EIA WTI forecast (Rigzone, Dec 2025)](https://www.rigzone.com/news/eia_again_raises_wti_price_forecast_for_both_2025_and_2026-16-dec-2025-182548-article/?rss=true)
- [OMB M-25-08, 2025 discount rates](https://bidenwhitehouse.archives.gov/wp-content/uploads/2025/01/M-25-08-2025-Discount-Rates-for-OMB-Circular-No.-A-94.pdf)
- [OMB M-25-23, A-94 status](https://www.whitehouse.gov/wp-content/uploads/2025/02/M-25-23-Rescission-and-Reinstatement-of-Circular-No.-A-94.pdf)
- DOE/PNNL, GAO and NASA: see `docs/research-external.md` (S1, S16, S2)

**Caveat on the oil price:** the $65.40 figure is EIA's estimate as reported by Rigzone, not EIA's final historical series. Check [EIA's spot price data](https://www.eia.gov/dnav/pet/hist/RWTCD.htm) before quoting it on a slide.

## 6. Presentation plan for the money slides

**Slide 5: "What it costs, what it's worth" (Nick, about 40 seconds)**
- **Left:** a cost stack bar, $168k parts program + $59.5k safety backlog = **$227.5k**, then $19.5k a year.
- **Right:** a cumulative cash line from month 0 to 36. It dips to about −$148k, crosses zero at **month 8**, and reaches **+$1.98M** by year 3.
- **Shade the band** between "everything goes wrong" (month 16) and "fast sign-off" (month 6).
- **Footnote:** "MODELED using the case's reduction fractions and contribution formula; margin, not cash; no repair savings claimed."
- **Say:** "For $227k, the plan pays for itself in about 8 months and is worth about $2M over three years. Even if everything goes wrong, it still pays back in 16 months. The biggest lever is closing the safety actions fast, which is why safety comes first."

**Slide 9: roadmap.** Put the Phase 2 numbers on it: +$134k, payback about 10–11 months after go-live, go/no-go at month 6.

**Q&A answers to rehearse**
- *"Is $842k real money?"* It's modeled contribution margin from the case's own formula, not booked cash. We claim no repair-cost savings.
- *"Why not ROI?"* The case says ROI isn't required. Payback and hours avoided are clearer, and we show both.
- *"What if oil drops?"* At about $50 WTI it still pays back in month 10.
- *"What does the AI chat cost?"* A few dollars a year in AI usage at our assumed volume. It's optional and outside the ask.
