"""Predict mechanical failures (bearing wear, seal leak) per asset and day from daily readings.

Only readings already received by the end of each day are used, so a score is what a planner could
have seen that day. Electrical trips, process upsets and unknown causes show no warning in the
readings (see `cause_precursors`), so the model does not claim to predict them.

Scenario data with one reading per asset per day: the hold-out numbers describe this dataset, not
production accuracy.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from casequest.clean import CleanData
from casequest.signals import NOISE_NOTE

MECHANICAL = ("Bearing wear", "Seal leak")
# Warnings show up about two days before a mechanical failure and not earlier (see `precursor_onset`).
HORIZON_DAYS = 3
LOOKBACK_DAYS = 2
TRAIN_END = pd.Timestamp("2025-07-01")  # fit on H1, report on H2
YEAR_START = pd.Timestamp("2025-01-01")
FEATURES = ("vib_last", "vib_max", "temp_max", "noise", "gap")


def daily_features(data: CleanData) -> pd.DataFrame:
    """One row per asset and day: evidence received by the end of that day over the last LOOKBACK_DAYS."""
    assets = data.assets.set_index("asset_id")
    r = data.readings
    days = pd.date_range(YEAR_START, r["observed_utc"].max().normalize(), freq="D")
    rows = []
    for aid, g in r.groupby("asset_id"):
        normal_v, normal_t = assets.loc[aid, "vibration_normal_mm_s"], assets.loc[aid, "temperature_normal_c"]
        obs = g["observed_utc"].to_numpy()
        recv = g["received_utc"].to_numpy()
        valid = (g["quality"].eq("Valid") & g["operating_state"].eq("Running")).to_numpy()
        vib = (g["vibration_mm_s"] / normal_v).to_numpy()
        temp = (g["temperature_c"] - normal_t).to_numpy()
        noise = g["inspection_note"].eq(NOISE_NOTE).to_numpy()
        for day in days:
            as_of = np.datetime64(day + pd.Timedelta(days=1))
            w = (recv < as_of) & (obs < as_of) & (obs >= as_of - np.timedelta64(LOOKBACK_DAYS, "D"))
            v = w & valid
            last = np.flatnonzero(v)
            rows.append({
                "asset_id": aid,
                "day": day,
                "vib_last": float(vib[last[np.argmax(obs[last])]]) if v.any() else 1.0,
                "vib_max": float(vib[v].max()) if v.any() else 1.0,
                "temp_max": float(temp[v].max()) if v.any() else 0.0,
                "noise": int(noise[w].sum()),
                "gap": int(not v.any()),
            })
    return pd.DataFrame(rows)


def label(features: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Adds `target` (a mechanical failure starts within HORIZON_DAYS after the day) and `stopped`
    (the asset is already down at the end of the day, so there is nothing to predict)."""
    u = events[events["event_type"] == "Unplanned"]
    out = features.copy()
    out["target"] = False
    out["stopped"] = False
    end = out["day"] + pd.Timedelta(days=1)
    for aid, g in u.groupby("asset_id"):
        rows = out["asset_id"] == aid
        for ev in g.itertuples():
            if ev.cause in MECHANICAL:
                out.loc[rows & (ev.start_utc > end) & (ev.start_utc <= end + pd.Timedelta(days=HORIZON_DAYS)), "target"] = True
            out.loc[rows & (ev.start_utc <= end) & (ev.end_utc > end), "stopped"] = True
    return out


@dataclass
class Logistic:
    """Plain logistic regression on standardized features, fit by Newton's method with a small ridge."""

    mean: np.ndarray
    scale: np.ndarray
    coef: np.ndarray
    intercept: float

    @classmethod
    def fit(cls, X: np.ndarray, y: np.ndarray, ridge: float = 1.0, iters: int = 50) -> Logistic:
        mean, scale = X.mean(axis=0), X.std(axis=0)
        scale[scale == 0] = 1.0
        Z = np.column_stack([np.ones(len(X)), (X - mean) / scale])
        w = np.zeros(Z.shape[1])
        penalty = np.eye(Z.shape[1]) * ridge
        penalty[0, 0] = 0.0
        for _ in range(iters):
            p = 1 / (1 + np.exp(-Z @ w))
            grad = Z.T @ (p - y) + penalty @ w
            hess = (Z * (p * (1 - p))[:, None]).T @ Z + penalty
            step = np.linalg.solve(hess, grad)
            w -= step
            if np.abs(step).max() < 1e-8:
                break
        return cls(mean=mean, scale=scale, coef=w[1:], intercept=float(w[0]))

    def predict(self, X: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-(self.intercept + ((X - self.mean) / self.scale) @ self.coef)))


def auc(y: np.ndarray, p: np.ndarray) -> float:
    """Probability that a random positive day scores above a random negative day."""
    ranks = pd.Series(p).rank().to_numpy()
    pos = y.astype(bool)
    n_pos, n_neg = pos.sum(), (~pos).sum()
    return float((ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


@dataclass
class Evaluation:
    auc: float
    threshold: float
    precision: float
    recall: float
    alerts: int
    base_rate: float
    events_caught: float
    median_lead_days: float


def evaluate(scored: pd.DataFrame, events: pd.DataFrame, threshold: float, period: slice) -> Evaluation:
    """Day-level AUC, precision and recall, plus the share of mechanical failures with at least one
    alert in the HORIZON_DAYS before they started, and how early the first alert came."""
    s = scored[(scored["day"] >= period.start) & (scored["day"] < period.stop) & ~scored["stopped"]]
    y, p = s["target"].to_numpy(), s["risk"].to_numpy()
    alert = p >= threshold
    u = events[(events["event_type"] == "Unplanned") & events["cause"].isin(MECHANICAL)]
    u = u[(u["start_utc"] >= period.start + pd.Timedelta(days=HORIZON_DAYS)) & (u["start_utc"] < period.stop)]
    alerts = s[alert]
    caught, leads = 0, []
    for ev in u.itertuples():
        a = alerts[(alerts["asset_id"] == ev.asset_id) & (alerts["day"] + pd.Timedelta(days=1) < ev.start_utc)
                   & (alerts["day"] + pd.Timedelta(days=1) >= ev.start_utc - pd.Timedelta(days=HORIZON_DAYS))]
        if len(a):
            caught += 1
            leads.append((ev.start_utc - (a["day"].min() + pd.Timedelta(days=1))).total_seconds() / 86400)
    return Evaluation(
        auc=round(auc(y, p), 3),
        threshold=threshold,
        precision=round(float(y[alert].mean()), 2) if alert.any() else float("nan"),
        recall=round(float(alert[y].mean()), 2) if y.any() else float("nan"),
        alerts=int(alert.sum()),
        base_rate=round(float(y.mean()), 3),
        events_caught=round(caught / len(u), 2) if len(u) else float("nan"),
        median_lead_days=round(float(np.median(leads)), 1) if leads else float("nan"),
    )


@dataclass
class Trained:
    model: Logistic
    scored: pd.DataFrame
    act_threshold: float
    cause_split: dict[str, dict[str, float]]
    # Share of training days in each level that really were followed by a mechanical failure.
    chance: dict[str, float]

    def level(self, risk: float) -> str:
        return "act" if risk >= self.act_threshold else "normal"


def choose_threshold(train: pd.DataFrame, min_precision: float) -> float:
    """Lowest risk cut-off whose training precision reaches `min_precision`, so alerts stay worth acting on."""
    y, p = train["target"].to_numpy(), train["risk"].to_numpy()
    for t in np.round(np.arange(0.05, 0.96, 0.01), 2):
        alert = p >= t
        if alert.sum() >= 10 and y[alert].mean() >= min_precision:
            return float(t)
    return 0.95


def mechanical_cause_split(data: CleanData) -> dict[str, dict[str, float]]:
    """Readings cannot tell bearing wear from a seal leak, so the likely cause is each asset type's 2025 mix."""
    u = data.events[(data.events["event_type"] == "Unplanned") & data.events["cause"].isin(MECHANICAL)]
    u = u.merge(data.assets[["asset_id", "asset_type"]], on="asset_id")
    mix = pd.crosstab(u["asset_type"], u["cause"], normalize="index").round(2)
    return {t: row.to_dict() for t, row in mix.iterrows()}


def train(data: CleanData) -> Trained:
    df = label(daily_features(data), data.events)
    fit_rows = df[(df["day"] < TRAIN_END) & ~df["stopped"]]
    model = Logistic.fit(fit_rows[list(FEATURES)].to_numpy(float), fit_rows["target"].to_numpy(float))
    df["risk"] = model.predict(df[list(FEATURES)].to_numpy(float))
    fit_rows = df[(df["day"] < TRAIN_END) & ~df["stopped"]]
    # One level only: a lower "watch" band scored below the base rate on training data, so it would be noise.
    act = choose_threshold(fit_rows, 0.5)
    chance = fit_rows.groupby(np.where(fit_rows["risk"] >= act, "act", "normal"))["target"].mean().round(2).to_dict()
    df["level"] = np.where(df["risk"] >= act, "act", "normal")
    return Trained(model=model, scored=df, act_threshold=act, cause_split=mechanical_cause_split(data), chance=chance)


def precursor_onset(data: CleanData, days: int = 6) -> pd.DataFrame:
    """Share of failures whose evidence window already showed vibration above 1.3x normal, k days before the start."""
    f = daily_features(data).set_index(["asset_id", "day"])
    u = data.events[data.events["event_type"] == "Unplanned"]
    rows = []
    for ev in u.itertuples():
        for k in range(1, days + 1):
            day = (ev.start_utc - pd.Timedelta(days=k)).normalize()
            if (ev.asset_id, day) in f.index:
                rows.append({"mechanical": ev.cause in MECHANICAL, "days_before": k, "warned": f.loc[(ev.asset_id, day), "vib_max"] > 1.3})
    return pd.DataFrame(rows).groupby(["days_before", "mechanical"])["warned"].mean().round(2).unstack()


def cause_precursors(data: CleanData) -> pd.DataFrame:
    """Mean evidence in the LOOKBACK_DAYS before each unplanned failure, by cause. Shows which causes warn."""
    f = daily_features(data).set_index(["asset_id", "day"])
    u = data.events[data.events["event_type"] == "Unplanned"]
    rows = []
    for ev in u.itertuples():
        day = (ev.start_utc - pd.Timedelta(days=1)).normalize()
        if (ev.asset_id, day) in f.index:
            rows.append({"cause": ev.cause, **f.loc[(ev.asset_id, day)].to_dict()})
    return pd.DataFrame(rows).groupby("cause")[list(FEATURES)].mean().round(2)
