# Phase 2: Data Audit

**Date:** 2026-10-23
**Status:** Complete. The cleaned data is reproducible, all 38 integrity and reconciliation checks pass, and all 48 automated tests pass. Audited by an independent skeptical reviewer (section 11).

> **Like I'm 5:** Someone handed us a box of puzzle pieces. Some pieces were in there twice, some had smudged labels, and a few were missing. In this phase we sorted the pieces, wiped the labels clean, and wrote down every single thing we did. Then we checked that the pieces actually fit together. They do.

---

## 1. Objective

Turn the messy workbook into trustworthy tables, without touching the original. Every change must be logged and backed by a rule from the ReadMe or Dictionary, and the result must be proven correct using the workbook's own formulas.

## 2. What was inspected

All six data tabs (Assets, Events, Production, Readings, Solutions, HSE), checked against the ReadMe and Dictionary rules that apply to cleaning. Rules for contribution margin, joins and HSE measures are applied in Phase 3.

## 3. What we built

| File | What it does | Like I'm 5 |
|---|---|---|
| `src/casequest/clean.py` | Cleaning rules, one function per table, each change logged | The sorting machine |
| `src/casequest/validate.py` | 38 checks: keys and grain, allowed category labels, 2025 date ranges, no negatives, and ReadMe/Dictionary formulas | The "do the pieces fit?" tester |
| `src/casequest/build.py` | Runs cleaning and checks, then writes the outputs | The on switch |
| `data/processed/*.csv` | 7 clean tables, including a new **Sites** table | The sorted pieces |
| `docs/cleaning-log.md` | Every rule, why it was applied, how many rows, and which records (generated) | The diary of what we changed |
| `docs/reconciliation.md` | Pass/fail for each check (generated) | The report card |
| `tests/` | 48 pytest tests: rule-by-rule unit tests, real-workbook tests, and mutation tests that corrupt data on purpose to prove the checks catch it | Robots that re-check our work every time |

**To rebuild everything:**

```bash
uv run python -m casequest.build
```

**To run the tests:**

```bash
uv run pytest
```

## 4. What was wrong with the data, and what we did

The full record-level detail is in [cleaning-log.md](cleaning-log.md).

| Problem | Count | Fix | Like I'm 5 |
|---|---:|---|---|
| Events: mixed asset IDs (`a010`, `8`, `A09`, `11`) | 8 rows | Normalized to `A###` | Same toy, but its name tag was scribbled |
| Events: duplicate rows (E0021, E0141) | 2 | Removed after proving they were identical in every column | Same piece counted twice |
| Events: missing `stopped_hours` | 4 | Rebuilt by adding up the five stages (the ReadMe rule). Only blank rows are filled; flagged `stopped_hours_recovered` | Missing total, so we added the parts back up |
| Events: pending parts invoices | 14 (12 unplanned, 2 planned) | **Kept as unknown, not zero.** `known_cost_usd` is blank for these; `known_cost_lower_bound_usd` counts labor + contractor only | A bill hasn't arrived yet. That doesn't mean it's free. |
| Assets: capacity written as `"22 bbl/hr"` | 3 | Kept just the number | — |
| Assets: site info repeated 3 times per site | 12 extra rows | Moved into a separate **Sites** table | So we don't pay for a site three times |
| Production: duplicate rows | 2 | Removed after verifying | — |
| Production: missing `potential_oil_bbl` | 3 | Recalculated as calendar hours × capacity (the ReadMe rule); flagged `potential_recovered` | — |
| Readings: repeated export rows | 6,594 rows (6,558 IDs appear twice, 12 appear four times) | Removed after verifying | Most of the bag was poured in twice |
| Readings: legacy `LEG-nnn` tags | 161 | Mapped to the asset; checked against the supplied `asset_id` for every row (the Dictionary mentions a TagMap, but the workbook has no TagMap tab); original tag kept | Old nickname matched to the real name |
| Readings: temperatures in °F | 4 | Converted to °C (e.g. 142.52 F → 61.40 C) | Wrong ruler |
| Readings: missing measurements | 339 | **Left missing.** No guessing. | We don't invent answers |
| Readings: `Suspect` flags | 58 | Kept, with the flag | "Hmm, weird," not "broken" |
| Readings: arrived late | 102 | Flagged. Timestamps left unchanged. | The letter came late, but what it says is still true |
| HSE: every row appears twice | 36 | Removed after verifying | — |
| Category labels (statuses, causes, quality flags…) | 0 variants today | Case/spacing variants mapped to the canonical label; **any unknown label stops the build** | A lowercase "open" must never sneak past the safety lock |
| Text whitespace | 0 cells today | Trimmed and logged (the count is logged even when it is zero) | — |

**Safety design:** the code **stops with an error** instead of guessing in all of these cases:
- two rows share an ID but differ anywhere
- `stopped_hours` contradicts the stage times
- tag mappings disagree
- a category label is unknown
- a capacity or temperature has an unexpected unit
- site fields disagree within a site
- the raw workbook's fingerprint has changed

If any check fails, the build refuses to write the processed tables. A person has to decide in those cases.

## 5. Proof it's right: 38 out of 38 checks pass

Full table: [reconciliation.md](reconciliation.md). The most important checks:

- Each outage's five stages add up to end time − start time (385 of 385). The supplied durations match the stages (381 of 381; the 4 recovered rows are excluded so the check isn't circular).
- Each outage's lost oil = hours stopped × capacity (385 of 385). This independently confirms the 4 recovered durations.
- Monthly lost oil in Production = the sum of every outage that month (216 of 216 asset-months)
- Production = potential − lost + recovered (216 of 216)
- Every HSE record links to a real outage on the same asset at the same time (36 of 36)

> **Like I'm 5:** We added up all the little outage numbers, and they equal the big monthly numbers exactly. The pieces fit, so we know we didn't lose or double any.

Mutation tests deliberately corrupt the data and confirm the checks catch each case, so the checks aren't a rubber stamp. The cases are: a production total, a duplicated reading day, a wrong labor crew, a wrong monthly price, a negative vibration, a broken site gate, a lowercase "open" and an unknown quality label.

## 6. Data observations that matter for later phases

These are **facts about data quality**, not recommendations yet.

| Observation | Evidence | Why it might matter |
|---|---|---|
| **Late arrivals occur only at Arroyo; missing readings broadly fall as network uptime rises** | Missing / late by site: Arroyo (92.8%) 135 / 102, Mesa (96.4%) 63 / 0, Prairie (97.4%) 59 / 0, Canyon (98.1%) 40 / 0, Juniper (99.5%) 23 / 0, Cedar (99.2%) 19 / 0 | Consistent with the Solutions rule that monitoring below 97% uptime needs edge buffering. The pattern is not perfectly monotonic. |
| 57 of 58 `Suspect` readings are vibration spikes | 16.1–27.9 mm/s, versus at most 7.8 mm/s on valid running readings. The other one (R06215) is a Stopped reading at 0.0 | Must not be treated as confirmed faults (Dictionary). |
| Operator notes exist at reading time | 254 "Operator noticed abnormal noise" notes | A possible early-warning signal. To be tested in Phase 3, using only data available before each outage. |
| Outage stage data is internally consistent | Checks above | Only arithmetic consistency. It says nothing about whether the Solutions reduction fractions are valid (the Dictionary says "No causal evidence"). |
| `technician_note` maps 1:1 to `cause` | 6 notes for 6 causes | Recorded after the event, so it must **not** be used as a predictor (that would leak the answer). |
| Every open HSE action is overdue | All 11 open actions were due by 2026-01-03; snapshot is 2026-10-01 | `is_overdue_critical` (open, severity 5, overdue) = 6 is the ReadMe's "overdue critical action count". |
| Net uncontained spill is zero | 6 contained spills: 4.8 bbl spilled, 4.8 bbl recovered | Cannot support any spill-reduction claim. |
| Cost records are incomplete for 14 events | `cost_complete = False` | Report maintenance cost as "at least $X" using `known_cost_lower_bound_usd`. |
| 18 events contain protected repair time (9 hours total) | Events | That time can never be reduced by any option. |

## 7. Assumptions and decisions

| # | Decision | Reason |
|---|---|---|
| D1 | An event's month = its start month | No events cross a month boundary (verified), and this matches the Dictionary's Production rule |
| D2 | "Delayed" ingestion = arrived more than 1 hour after observation | Normal lag is under 2 minutes; every delayed reading is about 30 hours late, so any threshold from 1 to 29 hours gives the same result |
| D3 | Processed CSVs are committed to git | So teammates without Python can use them in Excel or for slides. They are fully regenerated by the build, written with UTF-8 encoding and LF line endings (`.gitattributes`) so Windows rebuilds don't churn. |
| D4 | Suspect readings are kept | The Dictionary says Suspect ≠ fault. Each analysis decides whether to include them and says so. |

## 8. Open questions and risks

- **Q:** Should the prototype show Suspect readings? *Proposal:* show them greyed out, and exclude them from any alert logic.
- **Risk:** Teammates editing the CSVs by hand would break reproducibility. *Mitigation:* the files are labeled as generated; edit the code instead.

## 9. Acceptance criteria

- [x] Raw workbook unchanged (SHA-256 verified by a test)
- [x] Every cleaning change logged with its rule, reason, count and records
- [x] No imputation of measurements; unknown costs stay unknown
- [x] Conflicting duplicates would stop the build rather than be silently resolved
- [x] All 38 integrity and reconciliation checks pass, with no circular checks
- [x] All 48 automated tests pass, including mutation tests
- [x] Unknown labels, units and conflicting values stop the build
- [x] Independent skeptical audit completed and its findings fixed (section 11)
- [x] Outputs are reproducible with one command

## 10. Status and next step

**Phase 2 is done.**

**Next: Phase 3, business analysis.** Using the clean tables:
1. Downtime hours, lost oil and lost margin (with the ReadMe's contribution formula) by cause, stage, site and asset.
2. Maintenance cost, shown as a lower bound.
3. The HSE picture (overdue, severity-5 blocks, repeated hazards).
4. Whether readings and operator notes give an early warning before failures, tested only on data received before each outage.

The output will be a ranked problem list with evidence, ready for choosing the solution in Phase 4.

## 11. Independent audit

A separate Opus agent audited this branch with a skeptical brief. It was read-only, recomputed everything from the raw workbook with its own scripts, and ran mutation tests.

- **Verdict:** MERGE AFTER FIXES. No blockers.
- **Independent recomputation matched everything:** row counts, every changed cell, 6,598.55 unplanned hours, 165,679.12 bbl lost, $5,608,389.61 unplanned contribution loss, and the HSE gate (S02, S04, S06).
- **What we fixed in response:**
  - The HSE gate and categories are now guarded against case variants and unknown labels.
  - Circular checks are split, so recovered values are no longer checked against their own formula.
  - Added checks: one reading per asset per day of 2025, timestamps within 2025, Jan–Dec Production months, labor = repair × crew of 1 or 2, one price per month, no negative values.
  - `known_cost_usd` is now blank when parts are pending, with an explicit lower-bound column.
  - An explicit `No standalone reduction` token replaces "None", which pandas reads back as missing.
  - Added `is_overdue_critical` and a site-level `pilot_blocked`.
  - The build refuses to run if the raw file's hash has changed, and refuses to write tables if any check fails.
  - Reproducible output: rounded lag, pandas ≥ 3.0, UTF-8 and LF line endings, `.gitattributes`.
  - Stricter parsing of capacity and temperature units.
  - Whitespace trimming is now logged.
  - The doc claims above are corrected.
