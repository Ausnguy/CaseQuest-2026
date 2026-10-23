import math

import pandas as pd
import pytest

from casequest.clean import (
    CleaningLog,
    DataQualityError,
    clean_events,
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
        "cost_status": "Complete", "protected_repair_hours": 0.0,
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
    assert not out.loc[0, "cost_complete"]
    assert out.loc[0, "known_cost_usd"] == 3.0 * 85  # labor only; parts unknown
