"""Reconciliation and integrity checks: prove the cleaned tables obey the workbook's own rules."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from casequest.clean import CleanData
from casequest.config import CATEGORIES, SCENARIO_YEAR, STAGES

TOLERANCE = 0.02  # barrels / hours; source values are rounded to 2 dp

TABLE_ATTR = {"Assets": "assets", "Events": "events", "Readings": "readings", "HSE": "hse", "Solutions": "solutions"}

NON_NEGATIVE = {
    "assets": ["age_years", "modeled_capacity_bbl_hr", "vibration_normal_mm_s", "temperature_normal_c", "replacement_usd"],
    "events": [*STAGES, "stopped_hours", "lost_oil_bbl", "labor_hours", "parts_usd", "contractor_usd", "protected_repair_hours"],
    "production": ["calendar_hours", "potential_oil_bbl", "produced_oil_bbl", "gross_deferred_bbl", "recovered_oil_bbl", "price_usd_bbl", "variable_cost_usd_bbl"],
    "readings": ["vibration_mm_s"],
    "hse": ["action_setup_usd", "action_annual_usd", "action_person_hours", "spilled_oil_bbl", "recovered_spill_bbl"],
}


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _check(name: str, failures: int, total: int, rule: str, unit: str = "rows") -> Check:
    return Check(name, failures == 0, f"{total - failures}/{total} {unit} pass. Rule: {rule}")


def run_checks(data: CleanData) -> list[Check]:
    a, e, p, r, h = data.assets, data.events, data.production, data.readings, data.hse
    capacity = a.set_index("asset_id")["modeled_capacity_bbl_hr"]
    asset_ids = set(a["asset_id"])
    checks: list[Check] = []

    # --- Keys, grain and domains -------------------------------------------------------------
    checks.append(_check("Assets: 18 unique asset_id", int(a["asset_id"].duplicated().sum()) + abs(len(a) - 18), len(a), "Assets.asset_id is the primary key"))
    checks.append(_check("Sites: 6 sites", abs(len(data.sites) - 6), 6, "ReadMe scope: 6 sites", "sites"))
    checks.append(_check("Events: unique event_id and work_order_id", int(e["event_id"].duplicated().sum() + e["work_order_id"].duplicated().sum()), len(e), "Exactly one work order per event"))
    checks.append(_check("Events: asset_id exists in Assets", int((~e["asset_id"].isin(asset_ids)).sum()), len(e), "Foreign key to Assets"))
    months_2025 = pd.date_range(f"{SCENARIO_YEAR}-01-01", periods=12, freq="MS")
    expected_grid = pd.MultiIndex.from_product([sorted(asset_ids), months_2025])
    grid = pd.MultiIndex.from_frame(p[["asset_id", "month"]])
    checks.append(_check("Production: complete 18 x 12 grid for Jan-Dec 2025", len(expected_grid.symmetric_difference(grid)) + int(grid.duplicated().sum()), len(expected_grid), "Key is asset_id + month", "asset-months"))
    days_2025 = pd.date_range(f"{SCENARIO_YEAR}-01-01", f"{SCENARIO_YEAR}-12-31", freq="D")
    reading_days = pd.MultiIndex.from_arrays([r["asset_id"], r["observed_utc"].dt.normalize()])
    expected_days = pd.MultiIndex.from_product([sorted(asset_ids), days_2025])
    checks.append(_check("Readings: exactly one snapshot per asset per day of 2025", len(expected_days.symmetric_difference(reading_days)) + int(reading_days.duplicated().sum()) + int(r["reading_id"].duplicated().sum()), len(expected_days), "Daily 06:00 UTC snapshot", "asset-days"))
    checks.append(_check("HSE: unique hse_id", int(h["hse_id"].duplicated().sum()), len(h), "One observation per row"))

    for table, columns in CATEGORIES.items():
        df = getattr(data, TABLE_ATTR[table])
        bad = sum(int((~df[c].dropna().isin(allowed)).sum()) for c, allowed in columns.items())
        checks.append(_check(f"{table}: categorical values in allowed sets", bad, len(df), f"Allowed labels for {', '.join(columns)}"))
    sev_bad = int((~h["potential_severity"].between(1, 5)).sum() + (~h["likelihood_band"].between(1, 5)).sum())
    checks.append(_check("HSE: severity and likelihood bands within 1-5", sev_bad, len(h), "Dictionary ordinal bands 1-5"))

    year_bad = int((e["start_utc"].dt.year != SCENARIO_YEAR).sum() + (e["end_utc"].dt.year != SCENARIO_YEAR).sum() + (r["observed_utc"].dt.year != SCENARIO_YEAR).sum())
    checks.append(_check("Timestamps: event and reading times fall in 2025", year_bad, len(e) + len(r), "ReadMe scope: 2025 full year"))
    negatives = sum(int((getattr(data, t)[cols].fillna(0) < 0).sum().sum()) for t, cols in NON_NEGATIVE.items())
    checks.append(_check("All tables: no negative hours, volumes, costs or measures", negatives, sum(len(getattr(data, t)) for t in NON_NEGATIVE), "Physical quantities cannot be negative"))

    # --- Events internal formulas --------------------------------------------------------------
    stage_sum = e[STAGES].sum(axis=1)
    elapsed = (e["end_utc"] - e["start_utc"]).dt.total_seconds() / 3600
    supplied = e[~e["stopped_hours_recovered"]]
    checks.append(_check("Events: supplied stopped_hours = sum of five stages", int(((supplied["stopped_hours"] - stage_sum[supplied.index]).abs() > TOLERANCE).sum()), len(supplied), "Dictionary stopped_hours (excludes the recovered rows, which are filled by this formula)"))
    checks.append(_check("Events: sum of five stages = end_utc - start_utc", int(((elapsed - stage_sum).abs() > TOLERANCE).sum()), len(e), "Dictionary stopped_hours; independent of the recovered values"))
    expected_lost = (e["stopped_hours"] * e["asset_id"].map(capacity)).round(2)
    checks.append(_check("Events: lost_oil_bbl = stopped_hours x capacity (validates recovered durations)", int(((e["lost_oil_bbl"] - expected_lost).abs() > TOLERANCE).sum()), len(e), "Dictionary lost_oil_bbl"))
    opened_gap = ((e["opened_utc"] - e["start_utc"]).dt.total_seconds() / 3600 - e["detect_hours"]).abs()
    checks.append(_check("Events: opened = start + detect; closed = end", int((opened_gap > TOLERANCE).sum() + (e["closed_utc"] != e["end_utc"]).sum()), len(e), "Dictionary opened_utc / closed_utc"))
    crew = (e["labor_hours"] / e["repair_hours"]).round(6)
    checks.append(_check("Events: labor_hours = repair_hours x crew of 1 or 2", int((~crew.isin([1.0, 2.0])).sum()), len(e), "Dictionary labor_hours"))
    planned = e[e["event_type"] == "Planned"]
    checks.append(_check("Events: Planned has detect = 0 and recoverable = 0.25", int(((planned["detect_hours"] != 0) | (planned["recoverable_fraction"] != 0.25)).sum()), len(planned), "Dictionary detect_hours / recoverable_fraction"))
    checks.append(_check("Events: parts_usd blank exactly when invoice pending", int((e["parts_usd"].isna() != (e["cost_status"] == "Parts invoice pending")).sum()), len(e), "Dictionary parts_usd"))
    checks.append(_check("Events: protected_repair_hours <= repair_hours", int((e["protected_repair_hours"] > e["repair_hours"]).sum()), len(e), "ReadMe 'Overlap and safety': protected time is inside repair"))

    # --- Production reconciles to Events -------------------------------------------------------
    by_month = e.assign(recovered=e["lost_oil_bbl"] * e["recoverable_fraction"]).groupby(["asset_id", "month"]).agg(gross=("lost_oil_bbl", "sum"), recovered=("recovered", "sum"))
    merged = p.join(by_month, on=["asset_id", "month"]).fillna({"gross": 0.0, "recovered": 0.0})
    supplied_p = merged[~merged["potential_recovered"]]
    checks.append(_check("Production: supplied potential = calendar_hours x capacity", int(((supplied_p["potential_oil_bbl"] - supplied_p["calendar_hours"] * supplied_p["asset_id"].map(capacity)).abs() > TOLERANCE).sum()), len(supplied_p), "ReadMe 'Production' (excludes the recovered rows, which are filled by this formula)"))
    checks.append(_check("Production: gross_deferred = sum of event lost_oil (planned + unplanned)", int(((merged["gross_deferred_bbl"] - merged["gross"]).abs() > TOLERANCE).sum()), len(p), "ReadMe 'Production'"))
    checks.append(_check("Production: recovered = round(sum lost x recoverable, 2)", int(((merged["recovered_oil_bbl"] - merged["recovered"].round(2)).abs() > TOLERANCE).sum()), len(p), "ReadMe 'Production'"))
    produced = merged["potential_oil_bbl"] - merged["gross_deferred_bbl"] + merged["recovered_oil_bbl"]
    checks.append(_check("Production: produced = potential - gross + recovered (validates recovered potentials)", int(((merged["produced_oil_bbl"] - produced).abs() > TOLERANCE).sum()), len(p), "ReadMe 'Production'"))
    checks.append(_check("Production: price is the same for every asset in a month", int((p.groupby("month")["price_usd_bbl"].nunique() > 1).sum()), p["month"].nunique(), "Dictionary price_usd_bbl (monthly realized price)", "months"))
    checks.append(_check("Production: every event asset-month has a production row", int((~by_month.index.isin(grid)).sum()), len(by_month), "Needed to price event losses", "event asset-months"))

    # --- Readings ------------------------------------------------------------------------------
    tag_ok = r["asset_tag"].str.upper().str.extract(r"(\d+)$")[0].astype(int) == r["asset_id"].str[1:].astype(int)
    checks.append(_check("Readings: asset_tag number matches asset_id", int((~tag_ok).sum()), len(r), "Supplied asset_id mapping aid"))
    checks.append(_check("Readings: received_utc never before observed_utc", int((r["ingest_lag_hours"] < 0).sum()), len(r), "Dictionary received_utc"))
    checks.append(_check("Readings: no Fahrenheit-scale values remain (temp <= 120 C)", int((r["temperature_c"] > 120).sum()), len(r), "ReadMe 'Raw quality'"))
    is_missing = r["quality"] == "Missing"
    missing_ok = (is_missing == r["vibration_mm_s"].isna()) & (is_missing == r["temperature_c"].isna())
    checks.append(_check("Readings: quality = Missing exactly when vibration and temperature are blank", int((~missing_ok).sum()), len(r), "Dictionary quality / vibration_mm_s / temperature_c"))

    # --- HSE -----------------------------------------------------------------------------------
    linked = h.merge(e[["event_id", "asset_id", "start_utc"]], on="event_id", how="left", suffixes=("", "_event"))
    link_fail = linked["asset_id_event"].isna() | (linked["asset_id"] != linked["asset_id_event"]) | (linked["observed_utc"] != linked["start_utc"])
    checks.append(_check("HSE: event_id exists, same asset, same timestamp", int(link_fail.sum()), len(h), "HSE.event_id links to one outage"))
    site_ok = h["site_id"] == h["asset_id"].map(a.set_index("asset_id")["site_id"])
    checks.append(_check("HSE: site_id agrees with Assets", int((~site_ok).sum()), len(h), "Foreign key consistency"))
    status_ok = (h["action_status"] == "Closed") == h["closed_date"].notna()
    checks.append(_check("HSE: closed_date present exactly when Closed", int((~status_ok).sum()), len(h), "Dictionary closed_date"))
    checks.append(_check("HSE: closed actions carry no remaining cost", int(((h["action_status"] == "Closed") & (h["action_setup_usd"] + h["action_annual_usd"] + h["action_person_hours"] > 0)).sum()), len(h), "Dictionary action_setup_usd"))
    # Independent of the cleaning code's expression: "open" = no verified closure date; site via the asset.
    gate = data.sites.set_index("site_id")["pilot_blocked"]
    unclosed_sev5 = h[h["closed_date"].isna() & (pd.to_numeric(h["potential_severity"]) >= 5)]
    blocked_sites = set(unclosed_sev5["asset_id"].map(a.set_index("asset_id")["site_id"]))
    expected_gate = pd.Series([s in blocked_sites for s in gate.index], index=gate.index)
    checks.append(_check("Sites: pilot_blocked exactly where a severity-5 action lacks a verified closure date", int((gate != expected_gate).sum()), len(gate), "ReadMe 'HSE decision gate'; Dictionary closed_date null = open", "sites"))
    return checks
