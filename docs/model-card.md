# Failure model and parts plan

Code: `src/casequest/model.py` (prediction) and `src/casequest/maintenance.py` (parts, inventory, engineer timing). Tests: `tests/test_model.py`.

```bash
uv run python -m casequest.maintenance --as-of 2025-12-21   # one day's plan
uv run python -m casequest.maintenance --as-of 2025-12-21 --fill 100   # same day with the spares program fully stocked
uv run python -m casequest.maintenance --export   # writes data/model/predictions.json for the console and phone
```

## What it predicts

A **mechanical failure (bearing wear or seal leak) on an asset within the next 3 days**, from the readings received by the end of each day.

It does **not** predict electrical trips, process upsets or unknown causes. In the 7 days before those, vibration, temperature and operator notes look like any other day. Before bearing and seal failures they do not:

| Mean evidence the day before a failure | Vibration (× normal) | Temp above normal (°C) | Noise notes (2 days) |
|---|---|---|---|
| Bearing wear | 2.08 | 9.0 | 1.0 |
| Seal leak | 2.11 | 8.6 | 1.0 |
| Electrical trip | 1.16 | 2.8 | 0.0 |
| Process upset | 1.15 | 3.1 | 0.0 |
| Unknown | 1.15 | 3.1 | 0.0 |

Bearing and seal failures look the same in the readings, so the model cannot tell them apart. The likely cause shown is each asset type's 2025 mix (62–70% bearing, the rest seal), and the plan stages both kits.

The warning appears about **2 days** before a mechanical failure: 91% of them show vibration above 1.3× normal two days out, 1% three days out. That is why the evidence window is 2 days and the horizon is 3.

## Model

Logistic regression on five features per asset-day: latest valid vibration ratio, 2-day max vibration ratio, 2-day max temperature above normal, operator noise notes, and a no-valid-reading flag. Only Valid, Running readings count as sensor evidence; noise notes count whatever the sensor quality. Readings received after the day ends are excluded (tested).

- Fit on **2025-01-01 to 2025-06-30**. The alert threshold is the lowest score whose training precision reaches 50%.
- Scored on **2025-07-01 to 2025-12-31**, which the fit never saw.
- One alert level. A lower "watch" band was tried and dropped: only 3% of its days were followed by a failure, below the 9% base rate.

## Hold-out results (H2 2025)

| Measure | Value |
|---|---|
| AUC (asset-days) | 0.82 |
| Alerted days followed by a mechanical failure within 3 days | 68% (base rate 9%) |
| Mechanical failures with at least one alert before them | 90 of 91 |
| Median warning lead | 1.5 days |
| Failures warned early enough for a fresh parts order to land first | 82 of 91 |
| Parts-wait hours on mechanical failures a timely order would cover | 421 of 491 h (86%) |

The last two rows assume the order goes in at the first alert, with the site's observed parts lead time. They are an upper bound on what the plan could save, not a forecast.

This is scenario data with one reading per asset per day. These numbers describe how the model does on this dataset, not production accuracy.

## From a prediction to a plan

For every alerted asset, `make_plan` produces:

1. **Kits**: a bearing kit and a mechanical seal kit, each with its likelihood and the median 2025 parts invoice for that asset type.
2. **Shelf check**: is each kit on that site's shelf?
3. **Manager alert and order**: any kit not on the shelf is flagged to order now, with the site's lead time.
4. **Engineer timing**: leave when `parts ready − dispatch hours` has passed, so the engineer arrives as the last part lands. With everything on the shelf, they leave now.
5. **Tools**: lockout/tagout kit, the tools for each kit, plus controls for the site's open HSE findings (H2S detector, second-person isolation check, spill kit).

Every plan is advisory. A planner reviews it, and it never authorizes work or lifts an HSE hold.

### What comes from the data and what is modeled

| Input | Source |
|---|---|
| Parts lead time per site | Median `parts_wait_hours` of 2025 unplanned repairs that waited for parts (13–24 h) |
| Engineer travel per site | Median `dispatch_hours` (2.1–5.5 h) |
| Kit cost | Median `parts_usd` by cause and asset type |
| Open HSE findings | `hse` actions not closed |
| **Item-level stock** | **Modeled.** The workbook only gives a shelf fill % per site. Each site's critical-spares list is one kit per cause per asset (9 lines). A site at X% holds X% of the lines, bearing kits first, then seal, then electrical, High-criticality assets first. Arroyo (42%) holds 4 of 9. |
| Tools on hand | Not modeled. Tools are listed as a checklist the engineer takes from the maintenance base. |

## Output for the console and phone

`data/model/predictions.json` (about 460 KB):

- `meta`: what it predicts, what it does not, hold-out numbers.
- `days` and `levels`: per asset, one entry per day of 2025 (0 normal, 1 act), for the replay slider.
- `plans`: per day, the full plan for each alerted asset (kits, shelf, order, alert text, engineer timing, tools, HSE).
- `stock`, `sites`, `kit_cost_usd`: the modeled shelf, lead and travel times, kit prices.

Regenerate it after any change to the data or the model.

## Possible external validation

[Petrobras 3W](https://github.com/petrobras/3W) is a public dataset of real offshore oil-well events, including safety-valve failures. It would be the first outside check before relying on this approach at a real site. It is not used here: the case asks for the provided data.
