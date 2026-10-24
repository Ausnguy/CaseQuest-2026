"""From a failure prediction to a work plan: which kit, is it on the site shelf, what to order, when to send the engineer.

Run `uv run python -m casequest.maintenance --as-of 2025-10-15` for one day's plan, or `--export` to write
`data/model/predictions.json` for the console and the phone app.

What comes from the data: failure causes, the bearing/seal mix per asset type, parts cost, the hours a repair
waited for parts, dispatch and repair hours, site spare fill and open HSE actions.
What is modeled: item-level stock. The workbook only gives a shelf fill percentage per site, so a site at X%
is assumed to hold X% of its critical-spares lines, filled in priority order (`site_stock`).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field

import pandas as pd

from casequest.clean import CleanData, clean_all
from casequest.config import REPO_ROOT
from casequest.model import HORIZON_DAYS, MECHANICAL, TRAIN_END, YEAR_START, Trained, evaluate, train

KIT_FOR_CAUSE = {
    "Bearing wear": "Bearing kit",
    "Seal leak": "Mechanical seal kit",
    "Electrical trip": "Motor starter and relay kit",
}
KIT_PRIORITY = list(KIT_FOR_CAUSE.values())
TOOLS_FOR_KIT = {
    "Bearing kit": ["Bearing puller set", "Laser shaft alignment tool", "Torque wrench set"],
    "Mechanical seal kit": ["Seal installation tool set", "Torque wrench set", "Spill kit"],
    "Motor starter and relay kit": ["Insulation resistance tester", "Multimeter"],
}
# Every repair on rotating equipment starts with isolation; open findings add their own controls.
ALWAYS_TOOLS = ["Lockout/tagout kit"]
TOOLS_FOR_HAZARD = {
    "H2S monitoring": "Personal H2S gas detector",
    "Energy isolation / LOTO": "Second-person isolation verification",
    "Hydrocarbon containment": "Spill kit",
}
EXPORT_PATH = REPO_ROOT / "data" / "model" / "predictions.json"


def site_stock(data: CleanData, fill_override: float | None = None) -> dict[str, dict[str, dict[str, int]]]:
    """Modeled shelf: site -> asset -> kit -> units on hand (0 or 1).

    Each site's critical-spares list is one kit per failure cause per asset. Lines are filled most-used kit
    first (bearing, then seal, then electrical), High-criticality assets before Medium, until the share of
    lines stocked matches the site's spare fill. `fill_override` sets every site to one fill, e.g. 100 for
    the spares program at steady state.
    """
    rank = {"High": 0, "Medium": 1, "Low": 2}
    out: dict[str, dict[str, dict[str, int]]] = {}
    for site in data.sites.itertuples():
        assets = data.assets[data.assets["site_id"] == site.site_id]
        lines = sorted(
            ((KIT_PRIORITY.index(kit), rank.get(a.criticality, 3), a.asset_id, kit) for a in assets.itertuples() for kit in KIT_PRIORITY),
        )
        fill = site.spare_fill_pct if fill_override is None else fill_override
        stocked = round(len(lines) * fill / 100)
        shelf = {a: {kit: 0 for kit in KIT_PRIORITY} for a in assets["asset_id"]}
        for _, _, aid, kit in lines[:stocked]:
            shelf[aid][kit] = 1
        out[site.site_id] = shelf
    return out


@dataclass
class SiteTimes:
    parts_lead_hours: float
    dispatch_hours: float


def site_times(data: CleanData) -> dict[str, SiteTimes]:
    """Observed medians: hours a repair waited when parts were not on hand, and hours to get a technician there."""
    u = data.events[data.events["event_type"] == "Unplanned"].merge(data.assets[["asset_id", "site_id"]], on="asset_id", suffixes=("", "_a"))
    waited = u[u["parts_wait_hours"] > 0]
    fleet_lead = float(waited["parts_wait_hours"].median())
    out = {}
    for sid in data.sites["site_id"]:
        w = waited[waited["site_id"] == sid]["parts_wait_hours"]
        d = u[u["site_id"] == sid]["dispatch_hours"]
        out[sid] = SiteTimes(
            parts_lead_hours=round(float(w.median()) if len(w) >= 3 else fleet_lead, 1),
            dispatch_hours=round(float(d.median()), 1),
        )
    return out


def kit_cost(data: CleanData) -> dict[str, dict[str, float]]:
    """Median parts invoice per kit and asset type, from 2025 work orders with a known parts cost."""
    u = data.events[(data.events["event_type"] == "Unplanned") & data.events["parts_usd"].notna() & data.events["cause"].isin(KIT_FOR_CAUSE)]
    u = u.merge(data.assets[["asset_id", "asset_type"]], on="asset_id")
    med = u.groupby(["cause", "asset_type"])["parts_usd"].median().round(-1)
    out: dict[str, dict[str, float]] = {}
    for (cause, atype), usd in med.items():
        out.setdefault(KIT_FOR_CAUSE[cause], {})[atype] = float(usd)
    return out


@dataclass
class PartLine:
    kit: str
    for_cause: str
    likelihood: float
    on_shelf: bool
    order: bool
    lead_hours: float
    usd: float


@dataclass
class Plan:
    asset_id: str
    site_id: str
    asset_type: str
    day: str
    level: str
    chance: float
    evidence: dict[str, float]
    parts: list[PartLine]
    manager_alert: str | None
    engineer_leave_in_hours: float
    engineer_arrives_in_hours: float
    parts_ready_in_hours: float
    tools: list[str]
    hse_open: list[str]
    note: str = field(default="Advisory. A planner reviews it; it never authorizes work or lifts an HSE hold.")


def make_plan(
    asset: pd.Series,
    day: pd.Timestamp,
    level: str,
    chance: float,
    evidence: dict[str, float],
    cause_split: dict[str, float],
    shelf: dict[str, int],
    times: SiteTimes,
    costs: dict[str, dict[str, float]],
    hazards: list[str],
) -> Plan:
    """One asset's plan. Order whatever the likely causes need and the shelf lacks; send the engineer so they
    arrive as the last part lands, never before it and never later than needed."""
    parts = []
    for cause in MECHANICAL:
        kit = KIT_FOR_CAUSE[cause]
        on_shelf = shelf.get(kit, 0) > 0
        parts.append(PartLine(
            kit=kit,
            for_cause=cause,
            likelihood=cause_split.get(cause, 0.0),
            on_shelf=on_shelf,
            order=not on_shelf,
            lead_hours=0.0 if on_shelf else times.parts_lead_hours,
            usd=costs.get(kit, {}).get(asset["asset_type"], 0.0),
        ))
    missing = [p for p in parts if not p.on_shelf]
    ready = max((p.lead_hours for p in parts), default=0.0)
    leave = max(0.0, ready - times.dispatch_hours)
    alert = None
    if missing:
        kits = " and ".join(p.kit.lower() for p in missing)
        alert = f"{kits[0].upper() + kits[1:]} not on the {asset['site_name']} shelf. Order now: about {times.parts_lead_hours:g} h to arrive."
    tools = list(dict.fromkeys(ALWAYS_TOOLS + [t for p in parts for t in TOOLS_FOR_KIT[p.kit]] + [TOOLS_FOR_HAZARD[h] for h in hazards if h in TOOLS_FOR_HAZARD]))
    return Plan(
        asset_id=asset["asset_id"],
        site_id=asset["site_id"],
        asset_type=asset["asset_type"],
        day=day.strftime("%Y-%m-%d"),
        level=level,
        chance=chance,
        evidence=evidence,
        parts=parts,
        manager_alert=alert,
        engineer_leave_in_hours=round(leave, 1),
        engineer_arrives_in_hours=round(leave + times.dispatch_hours, 1),
        parts_ready_in_hours=round(ready, 1),
        tools=tools,
        hse_open=hazards,
    )


def open_hazards(data: CleanData) -> dict[str, list[str]]:
    h = data.hse[data.hse["action_status"] != "Closed"]
    return {sid: sorted(g["hazard"].unique()) for sid, g in h.groupby("site_id")}


def plans_for_day(data: CleanData, trained: Trained, day: pd.Timestamp, fill_override: float | None = None) -> list[Plan]:
    stock = site_stock(data, fill_override)
    times = site_times(data)
    costs = kit_cost(data)
    hazards = open_hazards(data)
    assets = data.assets.set_index("asset_id")
    s = trained.scored[(trained.scored["day"] == day.normalize()) & ~trained.scored["stopped"]]
    plans = []
    for row in s[s["level"] == "act"].sort_values("risk", ascending=False).itertuples():
        a = assets.loc[row.asset_id]
        asset = pd.Series({"asset_id": row.asset_id, "site_id": a["site_id"], "asset_type": a["asset_type"], "site_name": a["site_name"]})
        plans.append(make_plan(
            asset, day, row.level, trained.chance.get(row.level, 0.0),
            {"vibration_x_normal": round(row.vib_last, 2), "temp_above_normal_c": round(row.temp_max, 1), "noise_notes": int(row.noise)},
            trained.cause_split.get(a["asset_type"], {}), stock[a["site_id"]][row.asset_id], times[a["site_id"]], costs, hazards.get(a["site_id"], []),
        ))
    return plans


def export(data: CleanData, trained: Trained) -> dict:
    """Everything the console and phone need, precomputed per day so neither has to run the model."""
    holdout = evaluate(trained.scored, data.events, trained.act_threshold, slice(TRAIN_END, pd.Timestamp("2026-01-01")))
    s = trained.scored
    days = sorted(s["day"].unique())
    level_code = {"normal": 0, "act": 1}
    by_day: dict[str, list[dict]] = {}
    for day in days:
        plans = plans_for_day(data, trained, pd.Timestamp(day))
        if plans:
            by_day[pd.Timestamp(day).strftime("%Y-%m-%d")] = [asdict(p) for p in plans]
    return {
        "meta": {
            "predicts": f"Mechanical failure (bearing wear or seal leak) within {HORIZON_DAYS} days",
            "does_not_predict": "Electrical trips, process upsets and unknown causes: no warning shows in the readings before them",
            "trained_on": f"{YEAR_START.date()} to {(TRAIN_END - pd.Timedelta(days=1)).date()}",
            "holdout": {"period": f"{TRAIN_END.date()} to 2025-12-31", **asdict(holdout)},
            "chance_by_level": trained.chance,
            "stock_is_modeled": "Item-level stock is modeled from each site's spare fill %; the workbook has no item inventory",
        },
        "sites": {sid: asdict(t) for sid, t in site_times(data).items()},
        "stock": site_stock(data),
        "kit_cost_usd": kit_cost(data),
        "days": [pd.Timestamp(d).strftime("%Y-%m-%d") for d in days],
        "levels": {aid: [level_code[v] for v in g.sort_values("day")["level"]] for aid, g in s.groupby("asset_id")},
        "plans": by_day,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--as-of", default="2025-10-15", help="day to plan for (YYYY-MM-DD)")
    ap.add_argument("--fill", type=float, default=None, help="override every site's spare fill %%, e.g. 100")
    ap.add_argument("--export", action="store_true", help=f"write {EXPORT_PATH.relative_to(REPO_ROOT)}")
    args = ap.parse_args()
    data = clean_all()
    trained = train(data)
    if args.export:
        EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        EXPORT_PATH.write_text(json.dumps(export(data, trained), separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"Wrote {EXPORT_PATH.relative_to(REPO_ROOT)} ({EXPORT_PATH.stat().st_size // 1024} KB)")
        return 0
    day = pd.Timestamp(args.as_of)
    plans = plans_for_day(data, trained, day, args.fill)
    print(f"{day.date()}: {len(plans)} asset(s) flagged")
    for p in plans:
        print(f"\n{p.asset_id} {p.asset_type} at {p.site_id} · {p.level.upper()} · {round(p.chance * 100)}% chance of a mechanical failure within {HORIZON_DAYS} days")
        print(f"  evidence: {p.evidence}")
        for part in p.parts:
            state = "on shelf" if part.on_shelf else ("ORDER" if part.order else "not on shelf")
            print(f"  {part.kit} ({round(part.likelihood * 100)}% {part.for_cause.lower()}): {state}, ${part.usd:,.0f}")
        if p.manager_alert:
            print(f"  MANAGER: {p.manager_alert}")
        print(f"  engineer: leave in {p.engineer_leave_in_hours} h, arrive in {p.engineer_arrives_in_hours} h, parts ready in {p.parts_ready_in_hours} h")
        print(f"  tools: {', '.join(p.tools)}")
        if p.hse_open:
            print(f"  open HSE actions at site: {', '.join(p.hse_open)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
