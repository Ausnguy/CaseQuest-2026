"""Tests for metrics, the option model and the signal backtest on the real workbook."""

import pytest

from casequest.clean import clean_all
from casequest.config import STAGES
from casequest.metrics import enrich_events, summarize
from casequest.options import Plan, model_plan, sites_to_assets
from casequest.signals import backtest, vibration_alerts


@pytest.fixture(scope="module")
def data():
    return clean_all()


@pytest.fixture(scope="module")
def events(data):
    return enrich_events(data)


@pytest.fixture(scope="module")
def all_assets(data):
    return tuple(data.assets["asset_id"])


def test_contribution_loss_matches_readme_formula_for_one_event(events):
    ev = events.set_index("event_id").loc["E0002"]  # A001 January, planned
    expected = ev["lost_oil_bbl"] * (1 - ev["recoverable_fraction"]) * (ev["price_usd_bbl"] - ev["variable_cost_usd_bbl"])
    assert ev["contribution_loss_usd"] == pytest.approx(expected)


def test_unplanned_baseline_totals(events):
    u = summarize(events[events["event_type"] == "Unplanned"], "event_type").iloc[0]
    assert u["events"] == 313
    assert u["downtime_hours"] == pytest.approx(6598.6, abs=0.1)


def test_o4_avoids_sixty_percent_of_parts_wait(data, events, all_assets):
    r = model_plan(data, events, Plan("O4", {"O4": all_assets}))
    parts = events.loc[events["event_type"] == "Unplanned", "parts_wait_hours"].sum()
    assert r.avoided_hours == pytest.approx(0.6 * parts)


def test_o1_only_touches_mechanical_causes(data, events, all_assets):
    r = model_plan(data, events, Plan("O1", {"O1": all_assets}))
    touched = r.events.loc[r.events["avoided_hours"] > 0, "cause"].unique()
    assert set(touched) <= {"Bearing wear", "Seal leak"}


def test_protected_repair_time_is_never_reduced(data, events, all_assets):
    r = model_plan(data, events, Plan("O5", {"O5": all_assets}, fraction="high"))
    ev = r.events
    max_reducible = ev["repair_hours"] - ev["protected_repair_hours"]
    assert (ev["avoided_hours"] <= max_reducible + 1e-9).all()


def test_overlapping_options_multiply_not_add(data, events, all_assets):
    # O1 and O3 both reduce detection; combined detect remaining must be (1-0.6)(1-0.2), not 1-0.8
    r = model_plan(data, events, Plan("O1+O3", {"O1": all_assets, "O3": all_assets}))
    ev = r.events[r.events["cause"] == "Bearing wear"].iloc[0]
    remaining_detect = ev["detect_hours"] * 0.4 * 0.8
    assert ev["avoided_hours"] >= ev["detect_hours"] - remaining_detect - 1e-9


def test_o1_pulls_in_prerequisites_once(data, events, all_assets):
    r = model_plan(data, events, Plan("O1", {"O1": all_assets}))
    items = " ".join(r.cost_lines["item"])
    assert "O2" in items and "O6" in items and "cleanup" in items and "Edge" in items
    edge = r.cost_lines[r.cost_lines["item"].str.startswith("Edge")].iloc[0]
    assert edge["units"] == 2  # S02 (96.4%) and S04 (92.8%) are below 97%
    assert (r.cost_lines["item"].str.startswith("O2")).sum() == 1


def test_o4_needs_no_digital_prerequisites(data, events, all_assets):
    items = " ".join(model_plan(data, events, Plan("O4", {"O4": all_assets})).cost_lines["item"])
    assert "O2" not in items and "O6" not in items and "cleanup" not in items


def test_hse_gate_reported_only_for_sites_in_scope(data, events):
    safe = model_plan(data, events, Plan("safe", {"O4": sites_to_assets(data, ["S01", "S03", "S05"])}))
    risky = model_plan(data, events, Plan("risky", {"O4": sites_to_assets(data, ["S04"])}))
    assert safe.blocked_sites == []
    assert risky.blocked_sites == ["S04"]


def test_o5_restricted_to_pumps_and_adds_planned_outage(data, events, all_assets):
    r = model_plan(data, events, Plan("O5", {"O5": all_assets}))
    assert set(r.events.loc[r.events["avoided_hours"] > 0, "asset_type"]) <= {"Transfer pump", "Lift pump"}
    assert r.extra_planned_outage_hours == 6 * 12


def test_unknown_option_rejected(data, events):
    with pytest.raises(ValueError):
        model_plan(data, events, Plan("bad", {"O9": ("A001",)}))


def test_backtest_uses_only_received_data(data, events):
    b = backtest(data, events, vibration_alerts(data, 1.3), "vib", "H2")
    assert b.detection_by_cause["Bearing wear"] == 1.0
    assert b.detection_by_cause["Electrical trip"] == 0.0


def test_stage_columns_present(events):
    assert set(STAGES) <= set(events.columns)


def test_lead_time_follows_prerequisite_chain(data, events, all_assets):
    assert model_plan(data, events, Plan("O4", {"O4": all_assets})).lead_months == 1
    assert model_plan(data, events, Plan("O3", {"O3": all_assets})).lead_months == 3  # O6 (1) then O3 (2)
    assert model_plan(data, events, Plan("O1", {"O1": all_assets})).lead_months == 5  # O2 (2) then O1 (3)
