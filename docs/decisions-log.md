# Decisions and Q&A Log

This log is for the group. It lists every question Aayan asked, what we decided, and where the details live. Newest entries are last.

| # | Aayan asked | Answer / decision | Details |
|---:|---|---|---|
| 1 | Explain the packet, dataset and repo | Case summary, plus a list of the dirty-data issues | `docs/phase-1-discovery.md` |
| 2 | Work in phases as a senior PM/data/eng team, and explain it like I'm 5 | 8-phase process with a report per phase | `docs/phase-*.md` |
| 3 | Use the Sp00keee GitHub account | Done. That account has push access | — |
| 4 | Tech stack? | **Python + Streamlit** | `pyproject.toml` |
| 5 | Team roles | Aayan: everything · Nick: product · Austin: data · Wali: full-stack · Sidra: product. Everyone presents | `docs/team-plan.md` |
| 6 | Boring (spare parts) vs techy (monitoring)? I lean hybrid. Use fresh Sonnet graders and real research | Researched 18 sources. 3 AI graders ranked spare parts #1 (mean 86.7/105) and the hybrid #2 (84.3) | `docs/research-external.md`, `docs/grader-reports.md` |
| 7 | Audit everything with a skeptical Opus agent before `main` | Process adopted. Phase 2 took 4 audit rounds, Phases 3–5 took 2 | `docs/phase-2-data-audit.md` §11 |
| 8 | Which option? | **Option 2:** spare parts (O4) as the single primary; safety first; sensor-aware readiness feature in the app; sensors at Arroyo as a costed Phase 2 | `docs/phase-4-solution-selection.md` |
| 9 | Handoff for the group | `HANDOFF.md` | `HANDOFF.md` |
| 10 | Add a **site map that shows each site's issues**, plus an **AI chat** where field staff report missing or corroded parts from their phone for an operator to resolve on a PC. Good idea? | **Site map: yes, must-have.** **AI chat: yes, as a timeboxed nice-to-have with guardrails** (see below) | Below, and `docs/phase-5-product-design.md` §8 |
| 11 | Cost, benefit, payback "and all that jazz", with real sources, planned for the presentation | **$227.5k + $19.5k/yr. Payback in month 8. 3-year net about +$1.98M. Worst case pays back in month 16** | `docs/financial-case.md` |

## Entry 10 in full: site map and AI field-report chat

**Site map (must-have).**
- Six site markers, colored **HOLD** (red), **issues** (amber) or **OK** (green).
- Click a site to open a text box listing what's wrong and what happens next. For example: "HOLD: 2 overdue H2S/LOTO actions, awaiting supervisor verification · spare fill 42% · 3 readiness flags."
- It uses data we already have, so it's cheap to build and strong for the Tech score.

**AI field-report chat (nice-to-have; one person, 9:00–11:00, form fallback if it isn't working by 11:00).**
- **Flow:** a tech types on their phone, the AI fills in a structured ticket (site, machine, part, condition, urgency, photo), the tech confirms it, the ticket lands in the operator's queue on the PC, and the operator resolves it with a note.
- **Guardrails:**
  1. If the report mentions **corrosion, leaks, gas or pressure**, the chat says "Stop. Make the area safe and contact your HSE supervisor", flags the ticket red, and also routes it to HSE.
  2. The AI only **writes tickets**. It never orders parts, approves work, or touches LOTO or restart. The operator decides.
  3. Present it as the **parts-request channel of the spare-parts program**, not a second recommendation. It claims **zero** hours.
  4. Its cost is negligible: Claude Haiku 5.5 is about $2–25 a year in AI usage at the assumed volume. It's shown as optional, outside the ask.
  5. Offline queueing for weak signal; Arroyo has 92.8% network uptime.
  6. Report from a safe area, or use an intrinsically safe phone.
  7. Keep the API key out of the repo, and have a demo fallback form plus a backup video.
- **Demo moment:**
  1. A tech types "pump A012 at Arroyo, seal looks corroded and leaking."
  2. The chat replies with the safety stop message and builds a red ticket.
  3. The ticket appears in the operator queue, routed to HSE.
  4. Arroyo's map marker shows the new issue.
