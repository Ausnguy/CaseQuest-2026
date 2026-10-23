"""Reconciliation checks: prove the cleaned tables obey the workbook's own formulas."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from casequest.clean import CleanData
from casequest.config import STAGES

TOLERANCE = 0.02  # barrels / hours; source values are rounded to 2 dp


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _check(name: str, failures: int, total: int, rule: str) -> Check:
    return Check(name, failures == 0, f"{total - failures}/{total} rows pass. Rule: {rule}")


def run_checks(data: CleanData) -> list[Check]:
    a, e, p, r, h = data.assets, data.events, data.production, data.readings, data.hse
    capacity = a.set_index("asset_id")["modeled_capacity_bbl_hr"]
    asset_ids = set(a["asset_id"])
    checks: list[Check] = []

    # Keys and grain
    checks.append(_check("Assets: 18 unique asset_id", int(a["asset_id"].duplicated().sum()) + abs(len(a) - 18), len(a), "Assets.asset_id is the primary key"))
    checks.append(_check("Sites: 6 sites", abs(len(data.sites) - 6), 6, "ReadMe scope: 6 sites"))
    checks.append(_check("Events: unique event_id and work_order_id", int(e["event_id"].duplicated().sum() + e["work_order_id"].duplicated().sum()), len(e), "Exactly one work order per event"))
    checks.append(_check("Events: asset_id exists in Assets", int((~e["asset_id"].isin(asset_ids)).sum()), len(e), "Foreign key to Assets"))
    expected_grid = pd.MultiIndex.from_product([sorted(asset_ids), sorted(p["month"].unique())])
    grid = pd.MultiIndex.from_frame(p[["asset_id", "month"]])
    checks.append(_check("Production: complete 18 x 12 asset-month grid", len(expected_grid.symmetric_difference(grid)) + int(grid.duplicated().sum()), len(expected_grid), "Key is asset_id + month"))
    per_asset = r.groupby("asset_id").size()
    checks.append(_check("Readings: one snapshot per asset per day (365)", int((per_asset != 365).sum()) + int(r["reading_id"].duplicated().sum()), len(per_asset), "Daily 06:00 UTC snapshot"))
    checks.append(_check("HSE: unique hse_id", int(h["hse_id"].duplicated().sum()), len(h), "One observation per row"))

    # Events internal formulas
    stage_sum = e[STAGES].sum(axis=1)
    elapsed = (e["end_utc"] - e["start_utc"]).dt.total_seconds() / 3600
    checks.append(_check("Events: stopped_hours = sum of five stages = end - start", int(((e["stopped_hours"] - stage_sum).abs() > TOLERANCE).sum() + ((elapsed - stage_sum).abs() > TOLERANCE).sum()), len(e), "Dictionary stopped_hours"))
    expected_lost = (e["stopped_hours"] * e["asset_id"].map(capacity)).round(2)
    checks.append(_check("Events: lost_oil_bbl = stopped_hours x capacity", int(((e["lost_oil_bbl"] - expected_lost).abs() > TOLERANCE).sum()), len(e), "Dictionary lost_oil_bbl"))
    opened_gap = ((e["opened_utc"] - e["start_utc"]).dt.total_seconds() / 3600 - e["detect_hours"]).abs()
    checks.append(_check("Events: opened = start + detect; closed = end", int((opened_gap > TOLERANCE).sum() + (e["closed_utc"] != e["end_utc"]).sum()), len(e), "Dictionary opened_utc / closed_utc"))
    planned = e[e["event_type"] == "Planned"]
    checks.append(_check("Events: Planned has detect = 0 and recoverable = 0.25", int(((planned["detect_hours"] != 0) | (planned["recoverable_fraction"] != 0.25)).sum()), len(planned), "Dictionary detect_hours / recoverable_fraction"))
    checks.append(_check("Events: parts_usd blank exactly when invoice pending", int((e["parts_usd"].isna() != (e["cost_status"] == "Parts invoice pending")).sum()), len(e), "Dictionary parts_usd"))
    checks.append(_check("Events: protected_repair_hours <= repair_hours", int((e["protected_repair_hours"] > e["repair_hours"]).sum()), len(e), "ReadMe 'Overlap and safety': protected time is inside repair"))

    # Production reconciles to Events
    by_month = e.assign(recovered=e["lost_oil_bbl"] * e["recoverable_fraction"]).groupby(["asset_id", "month"]).agg(gross=("lost_oil_bbl", "sum"), recovered=("recovered", "sum"))
    merged = p.join(by_month, on=["asset_id", "month"]).fillna({"gross": 0.0, "recovered": 0.0})
    checks.append(_check("Production: potential = calendar_hours x capacity", int(((merged["potential_oil_bbl"] - merged["calendar_hours"] * merged["asset_id"].map(capacity)).abs() > TOLERANCE).sum()), len(p), "ReadMe 'Production'"))
    checks.append(_check("Production: gross_deferred = sum of event lost_oil (planned + unplanned)", int(((merged["gross_deferred_bbl"] - merged["gross"]).abs() > TOLERANCE).sum()), len(p), "ReadMe 'Production'"))
    checks.append(_check("Production: recovered = round(sum lost x recoverable, 2)", int(((merged["recovered_oil_bbl"] - merged["recovered"].round(2)).abs() > TOLERANCE).sum()), len(p), "ReadMe 'Production'"))
    produced = merged["potential_oil_bbl"] - merged["gross_deferred_bbl"] + merged["recovered_oil_bbl"]
    checks.append(_check("Production: produced = potential - gross + recovered", int(((merged["produced_oil_bbl"] - produced).abs() > TOLERANCE).sum()), len(p), "ReadMe 'Production'"))
    checks.append(_check("Production: every event month has a production row", int((~by_month.index.isin(grid)).sum()), len(by_month), "Needed to price event losses"))

    # Readings
    tag_ok = r["asset_tag"].str.upper().str.extract(r"(\d+)$")[0].astype(int) == r["asset_id"].str[1:].astype(int)
    checks.append(_check("Readings: asset_tag number matches asset_id", int((~tag_ok).sum()), len(r), "TagMap mapping aid"))
    checks.append(_check("Readings: received_utc never before observed_utc", int((r["ingest_lag_hours"] < 0).sum()), len(r), "Dictionary received_utc"))
    checks.append(_check("Readings: no Fahrenheit-scale values remain (temp <= 120 C)", int((r["temperature_c"] > 120).sum()), len(r), "ReadMe 'Raw quality'"))

    # HSE links
    linked = h.merge(e[["event_id", "asset_id", "start_utc"]], on="event_id", how="left", suffixes=("", "_event"))
    link_fail = linked["asset_id_event"].isna() | (linked["asset_id"] != linked["asset_id_event"]) | (linked["observed_utc"] != linked["start_utc"])
    checks.append(_check("HSE: event_id exists, same asset, same timestamp", int(link_fail.sum()), len(h), "HSE.event_id links to one outage"))
    site_ok = h["site_id"] == h["asset_id"].map(a.set_index("asset_id")["site_id"])
    checks.append(_check("HSE: site_id agrees with Assets", int((~site_ok).sum()), len(h), "Foreign key consistency"))
    status_ok = (h["action_status"] == "Closed") == h["closed_date"].notna()
    checks.append(_check("HSE: closed_date present exactly when Closed", int((~status_ok).sum()), len(h), "Dictionary closed_date"))
    checks.append(_check("HSE: closed actions carry no remaining cost", int(((h["action_status"] == "Closed") & (h["action_setup_usd"] + h["action_annual_usd"] + h["action_person_hours"] > 0)).sum()), len(h), "Dictionary action_setup_usd"))
    return checks
