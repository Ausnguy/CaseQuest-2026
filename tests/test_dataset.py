"""Integration tests against the real workbook, including mutation tests that prove the checks bite."""

import copy
import hashlib

import pytest

from casequest.clean import DataQualityError, clean_all, load_raw
from casequest.config import RAW_WORKBOOK, RAW_WORKBOOK_SHA256
from casequest.validate import run_checks


@pytest.fixture(scope="module")
def raw():
    return load_raw()


@pytest.fixture(scope="module")
def data(raw):
    return clean_all(raw)


@pytest.fixture
def fresh(data):
    """A deep copy that a test may corrupt without affecting others."""
    return copy.deepcopy(data)


def failed_names(data):
    return {c.name for c in run_checks(data) if not c.passed}


def test_raw_workbook_is_untouched(data):
    assert hashlib.sha256(RAW_WORKBOOK.read_bytes()).hexdigest() == RAW_WORKBOOK_SHA256


def test_clean_row_counts(data):
    counts = {name: len(df) for name, df in data.tables().items()}
    assert counts == {
        "assets": 18, "sites": 6, "events": 385, "production": 216,
        "readings": 6570, "solutions": 6, "hse": 36,
    }


def test_every_reconciliation_check_passes(data):
    failed = [f"{c.name}: {c.detail}" for c in run_checks(data) if not c.passed]
    assert failed == []


def test_event_counts_by_type(data):
    assert data.events["event_type"].value_counts().to_dict() == {"Unplanned": 313, "Planned": 72}


def test_only_missing_derived_values_are_recovered(data):
    assert data.events["stopped_hours_recovered"].sum() == 4
    assert data.production["potential_recovered"].sum() == 3


def test_hse_gate_matches_rule_on_real_data(data):
    open_sev5 = data.hse[(data.hse["action_status"] == "Open") & (data.hse["potential_severity"] == 5)]
    assert set(data.sites.loc[data.sites["pilot_blocked"], "site_id"]) == set(open_sev5["site_id"])
    assert data.hse["is_overdue_critical"].sum() == len(open_sev5)


def test_lowercase_status_in_raw_still_blocks_site(raw):
    mutated = {k: v.copy() for k, v in raw.items()}
    mutated["HSE"].loc[mutated["HSE"]["hse_id"].isin(["H007", "H008"]), "action_status"] = "open"
    sites = clean_all(mutated).sites
    assert sites.set_index("site_id").loc["S02", "pilot_blocked"]


def test_unexpected_category_in_raw_stops_build(raw):
    mutated = {k: v.copy() for k, v in raw.items()}
    mutated["Readings"].loc[0, "quality"] = "Questionable"
    with pytest.raises(DataQualityError):
        clean_all(mutated)


@pytest.mark.parametrize(
    "mutate, expected_failure",
    [
        (lambda d: d.production.__setitem__("gross_deferred_bbl", d.production["gross_deferred_bbl"] + (d.production.index == 0) * 50),
         "Production: gross_deferred = sum of event lost_oil (planned + unplanned)"),
        (lambda d: d.readings.__setitem__("observed_utc", d.readings["observed_utc"].where(d.readings.index != 4, d.readings["observed_utc"] + __import__("pandas").Timedelta(days=1))),
         "Readings: exactly one snapshot per asset per day of 2025"),
        (lambda d: d.events.__setitem__("labor_hours", d.events["labor_hours"] * ((d.events.index == 0) * 6 + 1)),
         "Events: labor_hours = repair_hours x crew of 1 or 2"),
        (lambda d: d.production.__setitem__("price_usd_bbl", d.production["price_usd_bbl"].where(d.production.index != 0, 9999)),
         "Production: price is the same for every asset in a month"),
        (lambda d: d.readings.__setitem__("vibration_mm_s", d.readings["vibration_mm_s"].where(d.readings.index != 1, -50.0)),
         "All tables: no negative hours, volumes, costs or measures"),
        (lambda d: d.sites.__setitem__("pilot_blocked", False),
         "Sites: pilot_blocked exactly where an open severity-5 action exists"),
    ],
    ids=["production-gross", "readings-duplicate-day", "labor-crew", "price-per-month", "negative-vibration", "site-gate"],
)
def test_checks_detect_corruption(fresh, mutate, expected_failure):
    mutate(fresh)
    assert expected_failure in failed_names(fresh)
