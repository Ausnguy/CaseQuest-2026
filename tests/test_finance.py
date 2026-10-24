"""Tests for the cash-flow / payback view."""

import pandas as pd
import pytest

from casequest.clean import clean_all
from casequest.finance import cash_flows, site_economics
from casequest.metrics import enrich_events
from casequest.options import Plan, model_plan
from casequest.roadmap import Wave, gate_first_waves


def test_simple_payback_and_totals():
    waves = [Wave("all", ("S01",), 0)]
    f = cash_flows(pd.Series({"S01": 120.0}), waves, site_setup_usd=0, site_annual_usd=0,
                   shared_upfront_usd=50.0, shared_annual_usd=0, months=12, annual_discount_rate=0.0)
    # 10/month benefit from month 1, 50 paid in month 1 -> cumulative -40, -30, ... reaches 0 in month 5
    assert f.payback_month == 5
    assert f.yearly.loc[0, "net_usd"] == pytest.approx(70.0)
    assert f.npv == pytest.approx(70.0)


def test_payback_none_when_never_positive():
    f = cash_flows(pd.Series({"S01": 0.0}), [Wave("w", ("S01",), 0)], 100, 0, 0, 0, months=12)
    assert f.payback_month is None


@pytest.fixture(scope="module")
def base():
    d = clean_all()
    e = enrich_events(d)
    r = model_plan(d, e, Plan("A", {"O4": tuple(d.assets["asset_id"])}))
    o4 = d.solutions.set_index("option_id").loc["O4"]
    hse = d.hse[d.hse["action_status"] == "Open"]
    se = site_economics(r, d)
    f = cash_flows(se["contribution_usd"], gate_first_waves(d, hse_verified_month=3), o4["setup_usd"], o4["annual_usd"],
                   hse["action_setup_usd"].sum(), hse["action_annual_usd"].sum())
    return r, se, f


def test_costs_reconcile_to_plan(base):
    r, _, f = base
    assert f.monthly["upfront_usd"].sum() == pytest.approx(r.upfront_usd)  # $227,500
    assert f.yearly.loc[1, "annual_cost_usd"] == pytest.approx(r.annual_usd)  # full year 2 = $19,500


def test_steady_state_benefit_matches_plan(base):
    r, se, f = base
    assert se["contribution_usd"].sum() == pytest.approx(r.avoided_contribution_usd)
    assert f.yearly.loc[1, "benefit_usd"] == pytest.approx(r.avoided_contribution_usd)


def test_base_case_payback_month(base):
    assert base[2].payback_month == 8
