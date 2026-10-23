import math

import pandas as pd
import pytest

from casequest.clean import (
    CleaningLog,
    DataQualityError,
    add_site_gate,
    clean_assets,
    clean_events,
    clean_hse,
    clean_production,
    drop_verified_duplicates,
    normalize_asset_id,
    parse_capacity,
    parse_temperature_c,
    resolve_reading_tag,
)


@pytest.mark.parametrize(
    "raw, expected",
    [("A001", "A001"), ("a010", "A010"), ("A09", "A009"), (8, "A008"), ("11", "A011"), ("  a003 ", "A003")],
)
def test_normalize_asset_id(raw, expected):
    assert normalize_asset_id(raw) == expected


@pytest.mark.parametrize("bad", ["", "B001", "pump", "A-1"])
def test_normalize_asset_id_rejects_garbage(bad):
    with pytest.raises(DataQualityError):
        normalize_asset_id(bad)


def test_resolve_reading_tag_handles_legacy_tags():
    assert resolve_reading_tag("LEG-001") == "A001"
    assert resolve_reading_tag("leg-018") == "A018"
    assert resolve_reading_tag("A005") == "A005"


@pytest.mark.parametrize("raw, expected", [("22 bbl/hr", 22.0), (16, 16.0), ("21.5 bbl/hr", 21.5)])
def test_parse_capacity(raw, expected):
    assert parse_capacity(raw) == expected


def test_parse_temperature_converts_fahrenheit_only():
    assert parse_temperature_c("142.52 F") == pytest.approx(61.4, abs=0.01)
    assert parse_temperature_c(64.1) == 64.1
    assert parse_temperature_c("61") == 61.0
    assert math.isnan(parse_temperature_c(None))


def test_drop_verified_duplicates_removes_identical_copies_and_logs():
    df = pd.DataFrame({"id": ["E1", "E1", "E2"], "v": [1, 1, 2]})
    log = CleaningLog()
    out = drop_verified_duplicates(df, "id", "T", log)
    assert out["id"].tolist() == ["E1", "E2"]
    assert log.entries[0].rows_affected == 1


def test_drop_verified_duplicates_refuses_conflicting_copies():
    df = pd.DataFrame({"id": ["E1", "E1"], "v": [1, 2]})
    with pytest.raises(DataQualityError, match="conflicting"):
        drop_verified_duplicates(df, "id", "T", CleaningLog())


def _event(**overrides):
    row = {
        "event_id": "E0001", "asset_id": "A001",
        "start_utc": pd.Timestamp("2025-01-06 12:00"), "end_utc": pd.Timestamp("2025-01-06 22:00"),
        "event_type": "Unplanned", "cause": "Seal leak",
        "detect_hours": 1.0, "dispatch_hours": 2.0, "parts_wait_hours": 3.0, "repair_hours": 3.0, "restart_hours": 1.0,
        "stopped_hours": 10.0, "lost_oil_bbl": 220.0, "recoverable_fraction": 0.2, "work_order_id": "W0001",
        "labor_hours": 3.0, "labor_rate_usd_hr": 85, "parts_usd": 1000.0, "contractor_usd": 0,
        "cost_status": "Complete", "work_type": "Corrective", "protected_repair_hours": 0.0,
    }
    row.update(overrides)
    return row


def test_clean_events_recovers_stopped_hours_from_stages():
    out = clean_events(pd.DataFrame([_event(stopped_hours=None)]), CleaningLog())
    assert out.loc[0, "stopped_hours"] == 10.0


def test_clean_events_rejects_stopped_hours_that_contradict_stages():
    with pytest.raises(DataQualityError):
        clean_events(pd.DataFrame([_event(stopped_hours=12.0)]), CleaningLog())


def test_pending_parts_cost_stays_unknown_not_zero():
    out = clean_events(pd.DataFrame([_event(parts_usd=None, cost_status="Parts invoice pending")]), CleaningLog())
    assert pd.isna(out.loc[0, "parts_usd"])
    assert pd.isna(out.loc[0, "known_cost_usd"])
    assert not out.loc[0, "cost_complete"]
    assert out.loc[0, "known_cost_lower_bound_usd"] == 3.0 * 85  # labor only; parts unknown


def test_supplied_stopped_hours_are_kept_not_overwritten():
    out = clean_events(pd.DataFrame([_event(stopped_hours=10.004)]), CleaningLog())
    assert out.loc[0, "stopped_hours"] == 10.004
    assert not out.loc[0, "stopped_hours_recovered"]


def test_category_case_variants_are_normalized_and_logged():
    log = CleaningLog()
    out = clean_events(pd.DataFrame([_event(event_type="unplanned", cause="SEAL  LEAK")]), log)
    assert out.loc[0, "event_type"] == "Unplanned"
    assert out.loc[0, "cause"] == "Seal leak"
    assert any("event_type" in e.rule for e in log.entries)


def test_unknown_category_stops_the_build():
    with pytest.raises(DataQualityError, match="cause"):
        clean_events(pd.DataFrame([_event(cause="Gremlins")]), CleaningLog())


@pytest.mark.parametrize("bad", ["20 bbl/day", "twenty"])
def test_parse_capacity_rejects_other_units(bad):
    with pytest.raises(DataQualityError):
        parse_capacity(bad)


@pytest.mark.parametrize("bad", ["61.4 C", "142.5°F", "hot"])
def test_parse_temperature_rejects_unknown_formats(bad):
    with pytest.raises(DataQualityError):
        parse_temperature_c(bad)


def _hse(**overrides):
    row = {
        "hse_id": "H001", "event_id": "E0001", "asset_id": "A001", "site_id": "S01",
        "observed_utc": pd.Timestamp("2025-01-06 12:00"), "hazard": "H2S monitoring", "outcome": "Near miss",
        "potential_severity": 5, "likelihood_band": 2, "control_gap": "x", "action_owner": "Site HSE supervisor",
        "due_date": "2025-02-05", "closed_date": None, "action_status": "Open",
        "action_setup_usd": 4500, "action_annual_usd": 500, "action_person_hours": 8,
        "spilled_oil_bbl": 0.0, "recovered_spill_bbl": 0.0, "status_as_of": "2026-10-01",
    }
    row.update(overrides)
    return row


def test_hse_gate_blocks_open_severity_five_even_if_lowercase():
    out = clean_hse(pd.DataFrame([_hse(action_status="open")]), CleaningLog())
    assert out.loc[0, "blocks_pilot"]
    assert out.loc[0, "is_overdue_critical"]


@pytest.mark.parametrize("overrides", [{"potential_severity": 3}, {"action_status": "Closed", "closed_date": "2025-01-20"}])
def test_hse_gate_ignores_low_severity_or_closed(overrides):
    out = clean_hse(pd.DataFrame([_hse(**overrides)]), CleaningLog())
    assert not out.loc[0, "blocks_pilot"]


def test_site_gate_marks_only_sites_with_blocking_actions():
    hse = clean_hse(pd.DataFrame([_hse(), _hse(hse_id="H002", site_id="S03", potential_severity=3)]), CleaningLog())
    assets = pd.DataFrame({"asset_id": ["A001"], "site_id": ["S01"]})
    sites = add_site_gate(pd.DataFrame({"site_id": ["S01", "S03"]}), hse.assign(asset_id="A001").iloc[:1], assets)
    assert sites["pilot_blocked"].tolist() == [True, False]


def _asset(asset_id, site_id, technicians=3):
    return {
        "asset_id": asset_id, "site_id": site_id, "asset_type": "Lift pump", "age_years": 5, "modeled_capacity_bbl_hr": 20,
        "criticality": "High", "vibration_normal_mm_s": 2.7, "temperature_normal_c": 62, "replacement_usd": 1,
        "site_name": "Cedar", "network_uptime_pct": 99.0, "technicians": technicians, "spare_fill_pct": 80,
        "training_hours_per_person": 12, "edge_setup_usd": 1, "edge_annual_usd": 1, "cleanup_setup_usd": 1, "available_project_hours": 100,
    }


def test_site_fields_that_disagree_within_a_site_stop_the_build():
    raw = pd.DataFrame([_asset("A001", "S01"), _asset("A002", "S01", technicians=4)])
    with pytest.raises(DataQualityError, match="Site fields differ"):
        clean_assets(raw, CleaningLog())


def test_production_recovers_missing_potential_and_flags_it():
    assets = pd.DataFrame({"asset_id": ["A001"], "modeled_capacity_bbl_hr": [22.0]})
    raw = pd.DataFrame([{"asset_id": "A001", "month": pd.Timestamp("2025-01-01"), "calendar_hours": 744, "potential_oil_bbl": None,
                         "produced_oil_bbl": 1.0, "gross_deferred_bbl": 0.0, "recovered_oil_bbl": 0.0, "price_usd_bbl": 70, "variable_cost_usd_bbl": 23.0}])
    out = clean_production(raw, assets, CleaningLog())
    assert out.loc[0, "potential_oil_bbl"] == 744 * 22
    assert out.loc[0, "potential_recovered"]


def test_blank_action_status_stops_the_build():
    with pytest.raises(DataQualityError, match="action_status is blank"):
        clean_hse(pd.DataFrame([_hse(action_status=None)]), CleaningLog())


def test_closed_without_verified_date_still_blocks():
    out = clean_hse(pd.DataFrame([_hse(action_status="Closed", closed_date=None)]), CleaningLog())
    assert out.loc[0, "blocks_pilot"]


@pytest.mark.parametrize("severity", ["5", " 5 ", 5.0])
def test_text_or_float_severity_is_coerced_and_still_blocks(severity):
    out = clean_hse(pd.DataFrame([_hse(potential_severity=severity)]), CleaningLog())
    assert out.loc[0, "blocks_pilot"]


@pytest.mark.parametrize("severity", ["5 - Severe", 6, None])
def test_invalid_severity_stops_the_build(severity):
    with pytest.raises(DataQualityError, match="potential_severity"):
        clean_hse(pd.DataFrame([_hse(potential_severity=severity)]), CleaningLog())


def test_ambiguous_snapshot_date_stops_the_build():
    with pytest.raises(DataQualityError):
        clean_hse(pd.DataFrame([_hse(status_as_of="01/10/2026")]), CleaningLog())
