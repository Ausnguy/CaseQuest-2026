"""Do daily readings warn before failures? Backtest using only data received before each outage.

This is a retrospective check on scenario data with daily snapshots. Per the Dictionary, it cannot
establish production-grade predictive accuracy.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from casequest.clean import CleanData

WINDOW_DAYS = 7
SPLIT_DATE = pd.Timestamp("2025-07-01")  # results reported per half-year; thresholds were explored on the full year, so H2 is NOT a true hold-out


def vibration_alerts(data: CleanData, multiple: float) -> pd.Series:
    """Valid, running readings whose vibration exceeds `multiple` x the asset's normal vibration."""
    normal = data.readings["asset_id"].map(data.assets.set_index("asset_id")["vibration_normal_mm_s"])
    r = data.readings
    return (r["quality"] == "Valid") & (r["operating_state"] == "Running") & (r["vibration_mm_s"] > multiple * normal)


@dataclass
class Backtest:
    rule: str
    period: str
    detection_by_cause: dict[str, float]
    detection_overall: float
    alerts: int
    precision: float
    median_lead_days: float


def backtest(data: CleanData, events: pd.DataFrame, alert: pd.Series, rule: str, period: str = "all") -> Backtest:
    """Detection: share of unplanned events with an alert observed in the prior WINDOW_DAYS and received before the start.
    Precision: share of alerts followed by an unplanned event on the same asset within WINDOW_DAYS."""
    r = data.readings[alert]
    u = events[events["event_type"] == "Unplanned"]
    if period == "H1":
        r, u = r[r["observed_utc"] < SPLIT_DATE], u[u["start_utc"] < SPLIT_DATE]
    elif period == "H2":
        r, u = r[r["observed_utc"] >= SPLIT_DATE], u[u["start_utc"] >= SPLIT_DATE]
    window = pd.Timedelta(days=WINDOW_DAYS)

    pairs = u[["event_id", "asset_id", "start_utc", "cause"]].merge(r[["asset_id", "observed_utc", "received_utc"]], on="asset_id")
    before = pairs[
        (pairs["observed_utc"] < pairs["start_utc"])
        & (pairs["observed_utc"] >= pairs["start_utc"] - window)
        & (pairs["received_utc"] < pairs["start_utc"])
    ]
    first = before.groupby("event_id")["observed_utc"].min()
    hit = u["event_id"].isin(first.index)
    lead = (u.set_index("event_id")["start_utc"] - first).dropna().dt.total_seconds() / 86400

    after = pairs[(pairs["start_utc"] > pairs["received_utc"]) & (pairs["start_utc"] <= pairs["observed_utc"] + window)]
    followed = r.reset_index().merge(after[["asset_id", "observed_utc"]].drop_duplicates(), on=["asset_id", "observed_utc"], how="left", indicator=True)
    precision = float((followed["_merge"] == "both").mean()) if len(r) else float("nan")

    return Backtest(
        rule=rule,
        period=period,
        detection_by_cause=hit.groupby(u["cause"]).mean().round(2).to_dict(),
        detection_overall=round(float(hit.mean()), 2),
        alerts=len(r),
        precision=round(precision, 2),
        median_lead_days=round(float(lead.median()), 1) if len(lead) else float("nan"),
    )


def random_alert_precision(data: CleanData, events: pd.DataFrame) -> float:
    """Share of asset-days that fall inside some pre-failure window: what a random alert would score."""
    u = events[events["event_type"] == "Unplanned"]
    r = data.readings[["asset_id", "observed_utc"]].reset_index()
    pairs = r.merge(u[["asset_id", "start_utc"]], on="asset_id")
    inside = pairs[(pairs["observed_utc"] < pairs["start_utc"]) & (pairs["observed_utc"] >= pairs["start_utc"] - pd.Timedelta(days=WINDOW_DAYS))]
    return round(inside["index"].nunique() / len(r), 2)


READINESS_MULTIPLE = 1.3  # vibration above 1.3x the asset's normal
READINESS_LOOKBACK_DAYS = 7
NOISE_NOTE = "Operator noticed abnormal noise"


def readiness_flags(data: CleanData, as_of: pd.Timestamp) -> pd.DataFrame:
    """Advisory 'pre-stage a bearing/seal kit' flags per asset, using only readings received by `as_of`.

    This is decision support for the spare-parts planner. It claims no downtime reduction, never authorizes
    work, and a qualified person reviews every flag. Vibration evidence uses Valid, Running readings only (Suspect
    and Missing are ignored). Operator "abnormal noise" notes are a human observation, so they count whatever the
    sensor quality flag on that day.
    """
    r = data.readings
    window = r[(r["received_utc"] <= as_of) & (r["observed_utc"] > as_of - pd.Timedelta(days=READINESS_LOOKBACK_DAYS))]
    vib_alert = vibration_alerts(data, READINESS_MULTIPLE).loc[window.index]
    noise = window["inspection_note"].eq(NOISE_NOTE)
    window = window.assign(vib_alert=vib_alert, noise=noise, valid_vibration=window["vibration_mm_s"].where(window["quality"] == "Valid"))
    by_asset = window.groupby("asset_id").agg(
        readings_received=("reading_id", "count"),
        vibration_alerts=("vib_alert", "sum"),
        noise_notes=("noise", "sum"),
        max_valid_vibration=("valid_vibration", "max"),
        last_received=("received_utc", "max"),
    )
    out = data.assets.set_index("asset_id")[["site_id", "asset_type", "criticality", "vibration_normal_mm_s"]].join(by_asset)
    out[["readings_received", "vibration_alerts", "noise_notes"]] = out[["readings_received", "vibration_alerts", "noise_notes"]].fillna(0).astype(int)
    out["flag"] = (out["vibration_alerts"] > 0) | (out["noise_notes"] > 0)
    out["data_gap"] = out["readings_received"] < READINESS_LOOKBACK_DAYS - 1
    out["suggestion"] = out["flag"].map({True: "Pre-stage bearing/seal kit; planner to review", False: ""})
    return out.reset_index()
