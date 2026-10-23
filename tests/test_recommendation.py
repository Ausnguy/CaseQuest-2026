"""Tests for the rollout model, readiness flags and KPI baselines."""

import pandas as pd
import pytest

from casequest.clean import clean_all
from casequest.metrics import enrich_events, kpi_baselines
from casequest.options import Plan, model_plan
from casequest.roadmap import Wave, first_year, gate_first_waves
from casequest.signals import readiness_flags


@pytest.fixture(scope="module")
def data():
    return clean_all()


@pytest.fixture(scope="module")
def site_hours(data):
    events = enrich_events(data)
    r = model_plan(data, events, Plan("A", {"O4": tuple(data.assets["asset_id"])}))
    return r.events.groupby("site_id")["avoided_hours"].sum()


def test_blocked_sites_go_live_only_after_hse_verification(data):
    waves = gate_first_waves(data, lead_months=1, hse_verified_month=3)
    blocked = set(data.sites.loc[data.sites["pilot_blocked"], "site_id"])
    for wave in waves:
        if blocked & set(wave.sites):
            assert wave.go_live_month >= 3 + 1
    assert waves[0].sites == ("S05",)
    assert waves[2].sites == ("S04",)  # largest blocked site first


def test_blocked_pilot_site_is_rejected(data):
    with pytest.raises(ValueError, match="blocked"):
        gate_first_waves(data, pilot_site="S04")


def test_first_year_prorates_by_live_months(site_hours):
    waves = [Wave("all", tuple(site_hours.index), 6)]
    assert first_year(site_hours, waves)["year1_hours"].sum() == pytest.approx(site_hours.sum() / 2)


def test_first_year_requires_every_site_in_a_wave(site_hours):
    with pytest.raises(ValueError, match="no wave"):
        first_year(site_hours, [Wave("one", ("S01",), 1)])


def test_slower_hse_verification_lowers_year_one(data, site_hours):
    fast = first_year(site_hours, gate_first_waves(data, hse_verified_month=1))["year1_hours"].sum()
    slow = first_year(site_hours, gate_first_waves(data, hse_verified_month=6))["year1_hours"].sum()
    assert slow < fast < site_hours.sum()


def test_readiness_ignores_readings_not_yet_received(data):
    delayed = data.readings[data.readings["delayed_ingest"]].iloc[0]
    as_of = delayed["observed_utc"] + pd.Timedelta(hours=1)  # observed but not yet received
    flags = readiness_flags(data, as_of).set_index("asset_id")
    window = data.readings[(data.readings["asset_id"] == delayed["asset_id"]) & (data.readings["received_utc"] <= as_of)
                           & (data.readings["observed_utc"] > as_of - pd.Timedelta(days=7))]
    assert flags.loc[delayed["asset_id"], "readings_received"] == len(window)
    assert delayed["reading_id"] not in set(window["reading_id"])


def test_readiness_ignores_suspect_spikes(data):
    suspect = data.readings[(data.readings["quality"] == "Suspect") & (data.readings["vibration_mm_s"] > 15)].iloc[0]
    as_of = suspect["received_utc"]
    flags = readiness_flags(data, as_of).set_index("asset_id")
    others = data.readings[(data.readings["asset_id"] == suspect["asset_id"]) & (data.readings["received_utc"] <= as_of)
                           & (data.readings["observed_utc"] > as_of - pd.Timedelta(days=7)) & (data.readings["quality"] == "Valid")]
    assert flags.loc[suspect["asset_id"], "max_vibration"] >= suspect["vibration_mm_s"]  # shown for context
    normal = data.assets.set_index("asset_id").loc[suspect["asset_id"], "vibration_normal_mm_s"]
    expected_alerts = int(((others["vibration_mm_s"] > 1.3 * normal) & (others["operating_state"] == "Running")).sum())
    assert flags.loc[suspect["asset_id"], "vibration_alerts"] == expected_alerts


def test_kpi_baselines_match_events(data):
    events = enrich_events(data)
    k = kpi_baselines(data, events[events["event_type"] == "Unplanned"]).set_index("site_id")
    assert k["unplanned_events"].sum() == 313
    assert k.loc["S04", "share_events_waiting_for_parts"] == pytest.approx(38 / 68)
    assert k["overdue_critical_hse_actions"].sum() == 6
