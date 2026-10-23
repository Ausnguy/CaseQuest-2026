"""Historical (observed 2025) performance metrics built on the clean tables.

Everything here describes what happened. Modeled future benefits live in options.py.
"""

from __future__ import annotations

import pandas as pd

from casequest.clean import CleanData
from casequest.config import STAGES


def enrich_events(data: CleanData) -> pd.DataFrame:
    """Events with asset/site context and the ReadMe contribution-margin loss.

    Contribution loss = lost_oil_bbl x (1 - recoverable_fraction) x (price - variable_cost)
    using the matching asset-month (ReadMe 'Contribution').
    """
    prices = data.production[["asset_id", "month", "price_usd_bbl", "variable_cost_usd_bbl"]]
    e = (
        data.events.merge(data.assets[["asset_id", "asset_type", "criticality", "modeled_capacity_bbl_hr"]], on="asset_id", validate="many_to_one")
        .merge(data.sites[["site_id", "site_name"]], on="site_id", validate="many_to_one")
        .merge(prices, on=["asset_id", "month"], how="left", validate="many_to_one")
    )
    if e["price_usd_bbl"].isna().any():
        raise ValueError("Some events have no matching production month for pricing")
    e["margin_usd_bbl"] = e["price_usd_bbl"] - e["variable_cost_usd_bbl"]
    e["unrecovered_bbl"] = e["lost_oil_bbl"] * (1 - e["recoverable_fraction"])
    e["contribution_loss_usd"] = e["unrecovered_bbl"] * e["margin_usd_bbl"]
    return e


def summarize(events: pd.DataFrame, by: str | list[str]) -> pd.DataFrame:
    """Count, hours, oil, contribution loss and known maintenance cost per group."""
    out = events.groupby(by).agg(
        events=("event_id", "count"),
        downtime_hours=("stopped_hours", "sum"),
        lost_oil_bbl=("lost_oil_bbl", "sum"),
        unrecovered_bbl=("unrecovered_bbl", "sum"),
        contribution_loss_usd=("contribution_loss_usd", "sum"),
        known_maintenance_lower_bound_usd=("known_cost_lower_bound_usd", "sum"),
        pending_invoices=("cost_complete", lambda s: int((~s).sum())),
        **{s: (s, "sum") for s in STAGES},
    )
    out["hours_share"] = out["downtime_hours"] / out["downtime_hours"].sum()
    out["loss_share"] = out["contribution_loss_usd"] / out["contribution_loss_usd"].sum()
    return out.sort_values("downtime_hours", ascending=False)


def stage_breakdown(events: pd.DataFrame) -> pd.DataFrame:
    hours = events[STAGES].sum()
    return pd.DataFrame({"hours": hours, "share": hours / hours.sum()})


def site_context(data: CleanData, unplanned: pd.DataFrame) -> pd.DataFrame:
    """Site resources next to site downtime and HSE status."""
    hse = data.hse
    open_actions = hse[hse["action_status"] == "Open"]
    hse_by_site = pd.DataFrame(
        {
            "open_hse_actions": open_actions.groupby("site_id").size(),
            "overdue_actions": hse[hse["is_overdue"]].groupby("site_id").size(),
            "open_action_setup_usd": open_actions.groupby("site_id")["action_setup_usd"].sum(),
            "open_action_hours": open_actions.groupby("site_id")["action_person_hours"].sum(),
        }
    )
    downtime = summarize(unplanned, "site_id")[["events", "downtime_hours", "contribution_loss_usd", "parts_wait_hours", "detect_hours", "dispatch_hours"]]
    out = data.sites.set_index("site_id").join(downtime).join(hse_by_site).fillna(0)
    return out.reset_index()  # pilot_blocked / open_sev5_actions come from clean.add_site_gate


def hse_summary(data: CleanData) -> dict:
    h = data.hse
    open_ = h[h["action_status"] == "Open"]
    repeated = h.groupby(["site_id", "hazard"]).size()
    return {
        "observations": len(h),
        "open_actions": len(open_),
        "overdue_open_actions": int(h["is_overdue"].sum()),
        "open_sev5_actions": int((open_["potential_severity"] == 5).sum()),
        "blocked_sites": sorted(h.loc[h["blocks_pilot"], "site_id"].unique()),
        "repeated_hazard_site_pairs": int((repeated > 1).sum()),
        "net_spill_bbl": float(h["net_spill_bbl"].sum()),
        "outcomes": h["outcome"].value_counts().to_dict(),
    }
