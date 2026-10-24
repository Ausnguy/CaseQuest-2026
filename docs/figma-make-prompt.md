# Figma Make Prompt for the 10 Slides

**How to use it:**
1. One person pastes the box below into Figma Make.
2. Check every number against `docs/presentation-plan.md`.
3. Fix slides with short follow-up prompts.
4. Present from Figma Make's full-screen preview, and **export a PDF backup** to submit at 4:45.

**Rules:**
- Never let Figma Make change a number.
- No real company logos or branding; the company is fictional.

```text
Build a 10-slide presentation deck as a single-page web app: 16:9 slides, full-screen, arrow keys and click to navigate, slide number bottom-right, a thin progress bar at the bottom. No logos of real companies.

AUDIENCE & TONE: Oil & gas operations, finance and HSE judges at a university case competition. Confident, consulting-style, minimal text: one bold headline sentence per slide, at most 3 short bullets, big numbers. Every number labeled OBSERVED (2025 data) or MODELED (estimate) with a small grey tag.

DESIGN SYSTEM: Background deep navy #14213D; text white; primary accent red #D62839; secondary amber #F4A261; success green #2A9D8F; muted grey #8D99AE. Font: Inter (headlines bold 44px, body 22px, stat numbers 72px). Generous whitespace, rounded cards (16px radius), card background #1D2D50. Charts: clean, minimal gridlines, labeled directly. Small speaker name + rubric tag top-right of each slide (grey, 14px).

COMPANY: Lone Mesa Energy (fictional oil producer), 6 sites: Cedar, Mesa, Juniper, Arroyo, Canyon, Prairie.

SLIDE 1 — tag "Business problem · Aayan"
Headline: "Our machines don't wait for repairs — they wait for parts. Arroyo waits most."
Three stat cards: "6,599 h unplanned downtime (2025)" · "24% of it waiting for parts (1,613 h)" · "6 overdue severity-5 safety actions".
Highlighted Arroyo card (red): "Arroyo: 30% of all downtime · 40% of parts-wait hours · $2.0M lost margin · locked out until safety actions close".

SLIDE 2 — tag "Data analysis · Austin"
Headline: "Six messy exports → clean, checked, reproducible."
Left list: "6,594 duplicate sensor rows removed" · "8 scrambled IDs fixed" · "4 °F temps converted" · "4 missing durations + 3 missing potentials rebuilt with the case formulas" · "339 missing readings left blank — never guessed" · "14 pending parts invoices kept unknown, not $0".
Right: green badge "39 / 39 checks pass · 99 automated tests · AI-agent skeptical audit (4 rounds)".
Footer (small): "Limits: synthetic data · daily snapshots · 6 sites (n=6)".

SLIDE 3 — tag "Data analysis · Austin"
Headline: "The emptier the shelf, the more breakdowns wait for parts."
Scatter chart, x "Spare parts on the shelf (%)" 40–100, y "Breakdowns that waited for parts (%)" 0–60, trend line, dots labeled:
Arroyo (42, 55.9) red and largest · Mesa (65, 37.5) · Prairie (70, 29.1) · Canyon (78, 21.7) · Cedar (86, 12.5) · Juniper (92, 10.0).
Callout: "r = −0.995 · a waiting breakdown loses ~16–18 h". Tag OBSERVED.

SLIDE 4 — tag "Technology · Wali"
Headline: "Existing data in → decisions by people out."
Left-to-right architecture with 6 boxes and arrows:
1 "Existing exports (sensor readings, work orders, HSE register)" → 2 "Clean + 39 checks" → 3 "Rules engine (stock-out risk, parts-readiness flags, safety gate, payback)" → 4 "Console app (site map, parts console, safety gate)" → 5 "People decide: planner approves pre-staging · HSE supervisor verifies closures" (green) → 6 "Audit log (append-only)".
Placeholder frame at the bottom for an app screenshot. Small note: "No new integration needed now; live integration is Phase 2."

SLIDE 5 — tag "Data storytelling · Aayan"
Headline: "Every number traces back."
4-step chain of cards with arrows:
"FINDING (OBSERVED): 24% of downtime is waiting for parts; empty shelves predict waits" → "ASSUMPTION (MODELED, case data): parts program cuts parts-wait 60% (range 35–75%)" → "RECOMMENDATION: critical spare parts at all 6 sites, safety first" → "BENEFIT (MODELED): 968 h/yr avoided (565–1,210); 666 h in year 1".
Small box "What we did NOT claim": "No injury/incident prevention · No repair-cost savings · No hours from sensors or AI".

SLIDE 6 — tag "Implementation · Sidra"
Headline: "12 months: safety first, pilot, expand only if it works."
Timeline months 0–12: "M0–3 Close 11 overdue safety actions (Site HSE supervisors)" · "M1 Pilot at Canyon (planner + storekeeper)" · "M2 Cedar + Juniper" · "M4 Arroyo (after safety verified)" · "M5 Mesa + Prairie" · "M6 Phase-2 sensor go/no-go" · "M9 review Cedar/Juniper".
Three pills for the Canyon pilot (leading KPI = spare fill %, baseline 78%): green "EXPAND: fill ≥ 90% at month 3, no safety bypass" · amber "REVISE: fill < 90% or waits not falling by month 6" · red "STOP: any safety bypass, or no improvement by month 6".
Footnote: "Training included in ~20 install hours per site (assumption)."

SLIDE 7 — tag "Recommendation & costs · Nick"
Headline: "One improvement: $227.5k upfront, $19.5k a year."
Left: stacked bar "Spare parts program, 6 sites $168k" + "Clear safety backlog $59.5k" (amber) = "$227.5k"; text "then $19.5k/yr".
Right cards: "968 h downtime avoided per year (MODELED, range 565–1,210)" · "666 h in year 1" · "Fits every site's staff hours".

SLIDE 8 — tag "Recommendation & costs · Nick"
Headline: "It pays for itself in about 8 months."
Line chart "Cumulative modeled margin, net of costs ($k)", x months 0–36, y −200 to 2,000, zero line emphasized. Points (month: $k): 0:0, 1:−88, 2:−137, 3:−123, 4:−138, 5:−148, 6:−80, 7:−11, 8:58, 9:126, 10:195, 11:263, 12:332, 18:743, 24:1155, 30:1566, 36:1978.
Red dot at the zero-crossing, label "Payback ≈ month 8". Light vertical band from month 6 to 16 labeled "best case ↔ everything goes wrong".
Right stats: "+$1.98M over 3 years" · "~8× benefit vs cost" · "Worst case still pays back by month 16".
Footnote: "MODELED contribution margin using the case formula — not cash. Case oil prices ($63–73/bbl) in line with EIA's ~$65 2025 WTI estimate (via Rigzone)."

SLIDE 9 — tag "Presentation · Aayan"
Headline: "Three reasons to say yes."
Three numbered cards: "1 · Targets the biggest fixable delay — parts waits, every site, every failure cause" · "2 · Cheap and fast — 1-month lead, pays back in ~8 months" · "3 · Safe by design — safety locks first, people make every decision".
Red banner: "The ask: approve $227.5k to start the safety sprint and the Canyon pilot next month."

SLIDE 10 — tag "HSE & security (bonus) · Sidra"
Headline: "It never trades safety for speed."
Four icon cards: "Hard safety gate — no site starts with an open severity-5 action; no override button" · "Speeds up waiting, never the work — lockout/tagout, gas monitoring and restart untouched" · "AI only advises — every sensor readiness flag is approved or rejected by a planner, overrides logged" · "Secure — role-based access, append-only log, no writes to source data, no keys in code".
Source line: "29 CFR 1910.147 · NIOSH/OSHA 2016-108 · NIST AI RMF · CISA AI-in-OT".
```

## Useful follow-up prompts
- "Make all headlines max 9 words without changing any numbers."
- "Slide 8: animate the line drawing left to right when the slide opens."
- "Add a presenter-notes panel toggled with the N key."
- "Increase contrast for a projector; minimum text 20px."
