# Grader Reports (condensed record)

**What these are:** three **AI grader agents** (Claude Sonnet). Each started from a fresh context and got identical instructions: grade strategies A–H against the CaseQuest rubric, check the ReadMe rules, find red flags, propose better variants and pick one. None was told the team's preference. They read the packet, the workbook ReadMe, the fact pack and the external research, and re-ran the model read-only.

**Limits:** they are **not human judges**. Their scores are internal decision support only, and must not be presented to the competition panel as independent validation. Their full reports live in the session transcript; this file keeps the scores and key arguments.

They graded the fact pack as of commit `e33473a`. Since then a few hybrid numbers moved slightly: O2 install hours are now charged to O1 sites, so G is $448,090 upfront with S04 +54 h. Strategy A is unchanged.

## Scores (out of 105)

| Strategy | Grader 1 | Grader 2 | Grader 3 | Mean |
|---|---:|---:|---:|---:|
| A. O4 spares, all sites | 88 | 84 | 88 | 86.7 |
| B. O1 monitoring | 84 | 78 | 84 | 82.0 |
| C. O3 workflow | 72 | 65 | 72 | 69.7 |
| D. O5 refurbishment | 54 | 48 | 53 | 51.7 |
| E. O4 + O3 | 83 | 77 | 80 | 80.0 |
| F. O4 + O1 all | 85 | 79 | 82 | 82.0 |
| G. O4 + O1 top-6 | 87 | 82 | 84 | 84.3 |
| H. O1 + O3 | 74 | 73 | 74 | 73.7 |

## Picks

| Grader | #1 | #2 | Confidence |
|---|---|---|---|
| 1 | A, phased by gate | G | medium |
| 2 | A, phased by gate ("V1") | G | medium |
| 3 | A, gate-first waves | B (B and G tied at 84; B named #2, G "only as O1 later") | medium |

## Arguments all three made
- **A has the best evidence-to-claim fit.**
  - The share of events waiting for parts tracks 1 − spare fill across sites (r ≈ −0.99).
  - Waits are all-or-nothing, at about 16–18 h when parts are missing.
  - A has the lowest cost per avoided hour, a 1-month lead, no prerequisites and no resource shortfall.
- **Hybrids risk being read as two recommendations.** The ReadMe says one primary plus *required* supporting options. Their hours are additive, so there is no synergy.
- **The sensor backtest is too clean** to present as proof: near-perfect detection and no false alarms, against field results of 0.76–0.92 detection and 0.08 false alarms. It does not validate the Solutions fractions.
- **Steady-state numbers must come with a year-1 figure,** because 76% of A's benefit sits at gated sites.
- **The HSE backlog should be shown separately.** The 6 severity-5 closures cost $33k and 48 h.
- **A's biggest risk is a capped Tech score** ("just inventory"). The fix is a real decision console with review, an HSE lock and an architecture view.
