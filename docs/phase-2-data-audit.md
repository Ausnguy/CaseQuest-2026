# Phase 2: Data Audit

**Date:** 2026-10-23
**Status:** Complete. The cleaned data is reproducible, every one of the 25 formula checks passes, and all 26 automated tests pass.

> **Like I'm 5:** Someone handed us a box of puzzle pieces. Some pieces were in there twice, some had smudged labels, and a few were missing. In this phase we sorted the pieces, wiped the labels clean, and wrote down every single thing we did. Then we checked that the pieces actually fit together. They do.

---

## 1. Objective

Turn the messy workbook into trustworthy tables, without touching the original. Every change must be logged and backed by a rule from the ReadMe or Dictionary, and the result must be proven correct using the workbook's own formulas.

## 2. What was inspected

All six data tabs (Assets, Events, Production, Readings, Solutions, HSE), checked against every rule in the ReadMe and every field definition in the Dictionary.

## 3. What we built

| File | What it does | Like I'm 5 |
|---|---|---|
| `src/casequest/clean.py` | Cleaning rules, one function per table, each change logged | The sorting machine |
| `src/casequest/validate.py` | 25 reconciliation checks based on the ReadMe formulas | The "do the pieces fit?" tester |
| `src/casequest/build.py` | Runs cleaning and checks, then writes the outputs | The on switch |
| `data/processed/*.csv` | 7 clean tables, including a new **Sites** table | The sorted pieces |
| `docs/cleaning-log.md` | Every rule, why it was applied, how many rows, and which records (generated) | The diary of what we changed |
| `docs/reconciliation.md` | Pass/fail for each check (generated) | The report card |
| `tests/` | 26 pytest tests: rule-by-rule unit tests plus tests on the real workbook | Robots that re-check our work every time |

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
| Events: missing `stopped_hours` | 4 | Rebuilt by adding up the five stages (the ReadMe rule) | Missing total, so we added the parts back up |
| Events: pending parts invoices | 14 | **Kept as unknown, not zero.** Flagged `cost_complete = False` | A bill hasn't arrived yet. That doesn't mean it's free. |
| Assets: capacity written as `"22 bbl/hr"` | 3 | Kept just the number | — |
| Assets: site info repeated 3 times per site | 12 extra rows | Moved into a separate **Sites** table | So we don't pay for a site three times |
| Production: duplicate rows | 2 | Removed after verifying | — |
| Production: missing `potential_oil_bbl` | 3 | Recalculated as calendar hours × capacity (the ReadMe rule) | — |
| Readings: the whole export appears twice | 6,594 rows | Removed after verifying | The whole bag of pieces was poured in twice |
| Readings: legacy `LEG-nnn` tags | 161 | Mapped to the asset; checked against the supplied mapping for every row; original tag kept | Old nickname matched to the real name |
| Readings: temperatures in °F | 4 | Converted to °C (e.g. 142.52 F → 61.40 C) | Wrong ruler |
| Readings: missing measurements | 339 | **Left missing.** No guessing. | We don't invent answers |
| Readings: `Suspect` flags | 58 | Kept, with the flag | "Hmm, weird," not "broken" |
| Readings: arrived late | 102 | Flagged. Timestamps left unchanged. | The letter came late, but what it says is still true |
| HSE: every row appears twice | 36 | Removed after verifying | — |

**Safety design:** if two rows share an ID but differ anywhere, the code **stops with an error** instead of quietly picking one. The same goes for `stopped_hours` values that contradict the stage times, and for tag mappings that disagree. A person has to decide in those cases.

## 5. Proof it's right: 25 out of 25 reconciliation checks pass

Full table: [reconciliation.md](reconciliation.md). The most important checks:

- Each outage's duration = detect + dispatch + parts wait + repair + restart = end time − start time (385 of 385)
- Each outage's lost oil = hours stopped × capacity (385 of 385)
- Monthly lost oil in Production = the sum of every outage that month (216 of 216 asset-months)
- Production = potential − lost + recovered (216 of 216)
- Every HSE record links to a real outage on the same asset at the same time (36 of 36)

> **Like I'm 5:** We added up all the little outage numbers, and they equal the big monthly numbers exactly. The pieces fit, so we know we didn't lose or double any.

A test also deliberately breaks one number and confirms the checks catch it, so the checks aren't a rubber stamp.

## 6. Data observations that matter for later phases

These are **facts about data quality**, not recommendations yet.

| Observation | Evidence | Why it might matter |
|---|---|---|
| **Missing and late sensor data concentrate at the sites with poor network uptime** | Arroyo (92.8% uptime): 135 missing readings and **all 102 late readings** (each about 30 hours late). Cedar (99.2%): 19 missing, 0 late. | Supports the Solutions rule that monitoring below 97% uptime needs edge buffering (Mesa and Arroyo). |
| `Suspect` readings are vibration spikes | Up to 27.9 mm/s, versus at most 7.8 mm/s on valid running readings | Must not be treated as confirmed faults (Dictionary). |
| Operator notes exist at reading time | 254 "Operator noticed abnormal noise" notes | A possible early-warning signal. To be tested in Phase 3, using only data available before each outage. |
| Outage stage times are exact sums | Checks above | Stage-level benefit modeling (the Solutions fractions) is well-founded. |
| Cost records are incomplete for 14 events | `cost_complete = False` | Report maintenance cost as "at least $X". |
| 18 events contain protected repair time (9 hours total) | Events | That time can never be reduced by any option. |

## 7. Assumptions and decisions

| # | Decision | Reason |
|---|---|---|
| D1 | An event's month = its start month | No events cross a month boundary (verified), and this matches the Dictionary's Production rule |
| D2 | "Delayed" ingestion = arrived more than 1 hour after observation | Normal lag is under 2 minutes; every delayed reading is about 30 hours late, so any threshold from 1 to 29 hours gives the same result |
| D3 | Processed CSVs are committed to git | So teammates without Python can use them in Excel or for slides. They are fully regenerated by the build. |
| D4 | Suspect readings are kept | The Dictionary says Suspect ≠ fault. Each analysis decides whether to include them and says so. |

## 8. Open questions and risks

- **Q:** Should the prototype show Suspect readings? *Proposal:* show them greyed out, and exclude them from any alert logic.
- **Risk:** Teammates editing the CSVs by hand would break reproducibility. *Mitigation:* the files are labeled as generated; edit the code instead.

## 9. Acceptance criteria

- [x] Raw workbook unchanged (SHA-256 verified by a test)
- [x] Every cleaning change logged with its rule, reason, count and records
- [x] No imputation of measurements; unknown costs stay unknown
- [x] Conflicting duplicates would stop the build rather than be silently resolved
- [x] All 25 ReadMe/Dictionary reconciliation checks pass
- [x] All 26 automated tests pass
- [x] Outputs are reproducible with one command

## 10. Status and next step

**Phase 2 is done.**

**Next: Phase 3, business analysis.** Using the clean tables:
1. Downtime hours, lost oil and lost margin (with the ReadMe's contribution formula) by cause, stage, site and asset.
2. Maintenance cost, shown as a lower bound.
3. The HSE picture (overdue, severity-5 blocks, repeated hazards).
4. Whether readings and operator notes give an early warning before failures, tested only on data received before each outage.

The output will be a ranked problem list with evidence, ready for choosing the solution in Phase 4.
