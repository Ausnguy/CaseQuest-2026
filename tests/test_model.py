"""Tests for the failure model and the parts/engineer plan on the real workbook."""

import pandas as pd
import pytest

from casequest.clean import clean_all
from casequest.maintenance import KIT_PRIORITY, SiteTimes, export, make_plan, plans_for_day, site_stock, site_times
from casequest.model import TRAIN_END, daily_features, evaluate, train


@pytest.fixture(scope="module")
def data():
    return clean_all()


@pytest.fixture(scope="module")
def trained(data):
    return train(data)


def test_features_ignore_readings_received_later(data):
    """A reading that arrives after the day ends must not change that day's features, only later days'."""
    day, next_day = pd.Timestamp("2025-03-10"), pd.Timestamp("2025-03-11")
    late = data.readings.copy()
    i = late.index[(late["asset_id"] == "A001") & (late["observed_utc"].dt.normalize() == day)][0]
    late.loc[i, ["vibration_mm_s", "quality", "operating_state", "received_utc"]] = [99.0, "Valid", "Running", next_day + pd.Timedelta(hours=12)]
    without = data.readings.drop(index=i)
    f_late = daily_features(type(data)(**{**data.__dict__, "readings": late})).set_index(["asset_id", "day"])
    f_without = daily_features(type(data)(**{**data.__dict__, "readings": without})).set_index(["asset_id", "day"])
    assert f_late.loc[("A001", day)].equals(f_without.loc[("A001", day)])
    assert f_late.loc[("A001", next_day), "vib_max"] == pytest.approx(99 / 2.7)


def test_holdout_beats_chance_by_a_wide_margin(data, trained):
    h2 = evaluate(trained.scored, data.events, trained.act_threshold, slice(TRAIN_END, pd.Timestamp("2026-01-01")))
    assert h2.auc > 0.75
    assert h2.precision > 4 * h2.base_rate
    assert h2.events_caught >= 0.9


def test_threshold_is_chosen_on_training_data_only(data):
    """Changing second-half labels must not move the threshold."""
    a = train(data)
    shuffled = data.events.copy()
    h2 = shuffled["start_utc"] >= TRAIN_END
    shuffled.loc[h2, "cause"] = "Unknown"
    b = train(type(data)(**{**data.__dict__, "events": shuffled}))
    assert a.act_threshold == b.act_threshold


def test_only_mechanical_causes_are_split(trained):
    for mix in trained.cause_split.values():
        assert set(mix) == {"Bearing wear", "Seal leak"}
        assert sum(mix.values()) == pytest.approx(1, abs=0.02)


def test_stock_follows_spare_fill(data):
    stock = site_stock(data)
    lines = {sid: sum(sum(k.values()) for k in shelf.values()) for sid, shelf in stock.items()}
    assert lines["S04"] == round(9 * 42 / 100)  # Arroyo, 42% fill
    assert lines["S03"] == round(9 * 92 / 100)
    assert all(v == 9 for v in {sid: sum(sum(k.values()) for k in s.values()) for sid, s in site_stock(data, 100).items()}.values())


def test_bearing_kits_are_stocked_before_seal_kits(data):
    for shelf in site_stock(data).values():
        bearing = sum(k["Bearing kit"] for k in shelf.values())
        seal = sum(k["Mechanical seal kit"] for k in shelf.values())
        assert bearing >= seal


def _plan(shelf):
    asset = pd.Series({"asset_id": "A012", "site_id": "S04", "asset_type": "Compressor", "site_name": "Arroyo"})
    return make_plan(asset, pd.Timestamp("2025-12-21"), "act", 0.67, {}, {"Bearing wear": 0.7, "Seal leak": 0.3},
                     shelf, SiteTimes(parts_lead_hours=16.5, dispatch_hours=5.5), {}, ["H2S monitoring"])


def test_missing_kit_alerts_the_manager_and_times_the_engineer_to_the_parts():
    p = _plan({"Bearing kit": 1, "Mechanical seal kit": 0})
    assert [x.kit for x in p.parts if x.order] == ["Mechanical seal kit"]
    assert "Order now" in p.manager_alert and "Arroyo" in p.manager_alert
    assert p.parts_ready_in_hours == 16.5
    assert p.engineer_leave_in_hours == 11.0
    assert p.engineer_arrives_in_hours == p.parts_ready_in_hours
    assert "Personal H2S gas detector" in p.tools and "Lockout/tagout kit" in p.tools


def test_full_shelf_means_no_order_and_the_engineer_goes_now():
    p = _plan({kit: 1 for kit in KIT_PRIORITY})
    assert not any(x.order for x in p.parts)
    assert p.manager_alert is None
    assert p.engineer_leave_in_hours == 0


def test_site_times_come_from_observed_events(data):
    t = site_times(data)
    assert set(t) == set(data.sites["site_id"])
    assert all(v.parts_lead_hours > 0 and v.dispatch_hours > 0 for v in t.values())


def test_plans_and_export_agree(data, trained):
    day = trained.scored[(trained.scored["level"] == "act") & ~trained.scored["stopped"]]["day"].iloc[0]
    plans = plans_for_day(data, trained, day)
    assert plans and all(p.level == "act" for p in plans)
    out = export(data, trained)
    assert len(out["plans"][day.strftime("%Y-%m-%d")]) == len(plans)
    assert set(out["levels"]) == set(data.assets["asset_id"])
    assert all(len(v) == len(out["days"]) for v in out["levels"].values())
