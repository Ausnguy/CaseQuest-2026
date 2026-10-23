"""Model an intervention plan with the Solutions sheet and ReadMe rules.

A Plan says which options run on which assets. This module applies:
- eligibility (causes, asset types) and stage reductions (base/low/high)
- overlap: remaining stage = original x product(1 - reductions); protected repair time is never reduced
- dependencies: O1 needs O2 (once per org), O6 + site cleanup per site, and edge buffering below 97% network uptime;
  O3 needs O6 + site cleanup per site. Shared prerequisites are paid once.
- open HSE actions at in-scope sites (cost and hours) and the severity-5 pilot gate
- resource load versus each site's available project hours

All outputs are modeled estimates, not observed results.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from casequest.clean import CleanData
from casequest.config import NO_STANDALONE_REDUCTION

STAGE_KEYS = {
    "detect_hours": "detect",
    "dispatch_hours": "dispatch",
    "parts_wait_hours": "parts_wait",
    "repair_hours": "repair",
    "restart_hours": "restart",
}
EDGE_UPTIME_THRESHOLD = 97.0
O5_EXTRA_PLANNED_HOURS = 6.0
NEEDS_SITE_PREREQS = {"O1", "O3"}  # O6 training + site cleanup


@dataclass(frozen=True)
class Plan:
    name: str
    scope: dict[str, tuple[str, ...]]  # option_id -> asset_ids it is deployed on
    fraction: str = "base"  # base | low | high
    extra_help_rate_usd_hr: float = 85.0  # assumption: fully loaded internal labor rate from Events


@dataclass
class PlanResult:
    plan: Plan
    avoided_hours: float
    avoided_bbl: float
    avoided_contribution_usd: float
    baseline_hours: float
    upfront_usd: float
    annual_usd: float
    cost_lines: pd.DataFrame
    site_resources: pd.DataFrame
    blocked_sites: list[str]
    extra_planned_outage_hours: float
    lead_months: int
    events: pd.DataFrame = field(repr=False)

    @property
    def avoided_share(self) -> float:
        return self.avoided_hours / self.baseline_hours if self.baseline_hours else 0.0


def _split(text: str) -> set[str]:
    return {part.strip() for part in str(text).split(";") if part.strip()}


def _option_applies(option: pd.Series, events: pd.DataFrame) -> pd.Series:
    causes = str(option["eligible_causes"])
    if causes == "All unplanned":
        cause_ok = pd.Series(True, index=events.index)
    elif causes == NO_STANDALONE_REDUCTION:
        cause_ok = pd.Series(False, index=events.index)
    else:
        cause_ok = events["cause"].isin(_split(causes))
    types = str(option["applicable_types"])
    type_ok = pd.Series(True, index=events.index) if types == "All" else events["asset_type"].isin(_split(types))
    return cause_ok & type_ok


def sites_to_assets(data: CleanData, site_ids, asset_types=None) -> tuple[str, ...]:
    a = data.assets[data.assets["site_id"].isin(site_ids)]
    if asset_types:
        a = a[a["asset_type"].isin(asset_types)]
    return tuple(sorted(a["asset_id"]))


def model_plan(data: CleanData, enriched_events: pd.DataFrame, plan: Plan) -> PlanResult:
    solutions = data.solutions.set_index("option_id")
    unknown = set(plan.scope) - set(solutions.index)
    if unknown:
        raise ValueError(f"Unknown option(s): {sorted(unknown)}")

    events = enriched_events[enriched_events["event_type"] == "Unplanned"].copy()
    keep = {stage: pd.Series(1.0, index=events.index) for stage in STAGE_KEYS}
    for option_id, assets in plan.scope.items():
        option = solutions.loc[option_id]
        applies = _option_applies(option, events) & events["asset_id"].isin(assets)
        for stage, key in STAGE_KEYS.items():
            fraction = float(option[f"{key}_{plan.fraction}"])
            keep[stage] = keep[stage].where(~applies, keep[stage] * (1 - fraction))

    avoided = pd.Series(0.0, index=events.index)
    for stage in STAGE_KEYS:
        reducible = events[stage] - (events["protected_repair_hours"] if stage == "repair_hours" else 0.0)
        avoided += reducible * (1 - keep[stage])
    events["avoided_hours"] = avoided
    events["avoided_bbl"] = events["avoided_hours"] * events["modeled_capacity_bbl_hr"]
    events["avoided_contribution_usd"] = events["avoided_bbl"] * (1 - events["recoverable_fraction"]) * events["margin_usd_bbl"]

    cost_lines, site_resources = _costs_and_resources(data, solutions, plan)
    scope_sites = set(site_resources["site_id"])
    blocked = sorted(set(data.sites.loc[data.sites["pilot_blocked"], "site_id"]) & scope_sites)
    asset_type = data.assets.set_index("asset_id")["asset_type"]
    o5_assets = [a for a in plan.scope.get("O5", ()) if asset_type[a] in _split(solutions.loc["O5", "applicable_types"])]
    lead = critical_path_months(solutions, _all_options(plan))

    return PlanResult(
        plan=plan,
        avoided_hours=float(events["avoided_hours"].sum()),
        avoided_bbl=float(events["avoided_bbl"].sum()),
        avoided_contribution_usd=float(events["avoided_contribution_usd"].sum()),
        baseline_hours=float(events["stopped_hours"].sum()),
        upfront_usd=float(cost_lines["upfront_usd"].sum()),
        annual_usd=float(cost_lines["annual_usd"].sum()),
        cost_lines=cost_lines,
        site_resources=site_resources,
        blocked_sites=blocked,
        extra_planned_outage_hours=O5_EXTRA_PLANNED_HOURS * len(o5_assets),
        lead_months=lead,
        events=events,
    )


PREREQUISITES = {"O1": ("O2", "O6"), "O3": ("O6",)}  # ReadMe 'Dependencies'; site cleanup has no lead time


def critical_path_months(solutions: pd.DataFrame, options) -> int:
    """Months until every option is commissioned, assuming an option starts only after its prerequisites
    are commissioned and independent options run in parallel (an assumption for the roadmap)."""
    lead = solutions["lead_months"].astype(int)

    def finish(option: str) -> int:
        return lead[option] + max((finish(p) for p in PREREQUISITES.get(option, ())), default=0)

    return max(finish(o) for o in options)


def _all_options(plan: Plan) -> list[str]:
    options = [o for o, assets in plan.scope.items() if assets]
    if "O1" in options and "O2" not in options:
        options.append("O2")
    if NEEDS_SITE_PREREQS & set(options) and "O6" not in options:
        options.append("O6")
    return options


def _costs_and_resources(data: CleanData, solutions: pd.DataFrame, plan: Plan) -> tuple[pd.DataFrame, pd.DataFrame]:
    site_of = data.assets.set_index("asset_id")["site_id"]
    sites = data.sites.set_index("site_id")
    deployed = {o: tuple(a) for o, a in plan.scope.items() if a}
    sites_for = {o: sorted({site_of[a] for a in assets}) for o, assets in deployed.items()}
    scope_sites = sorted({s for ss in sites_for.values() for s in ss})
    prereq_sites = sorted({s for o in NEEDS_SITE_PREREQS & set(deployed) for s in sites_for[o]})
    monitored_sites = sites_for.get("O1", [])

    lines: list[dict] = []
    hours = pd.Series(0.0, index=scope_sites)

    def add(item, units, setup, annual, site_hours=None, note=""):
        lines.append({"item": item, "units": units, "upfront_usd": setup, "annual_usd": annual, "note": note})
        if site_hours is not None:
            for site, h in site_hours.items():
                hours[site] += h

    for option_id, assets in deployed.items():
        if option_id in ("O2", "O6"):
            continue  # handled as prerequisites below so they are paid once
        opt = solutions.loc[option_id]
        unit = opt["billing_unit"]
        if unit == "Asset":
            n = len(assets)
            per_site = pd.Series([site_of[a] for a in assets]).value_counts() * opt["install_person_hours"]
        elif unit == "Site":
            n = len(sites_for[option_id])
            per_site = pd.Series(opt["install_person_hours"], index=sites_for[option_id])
        else:
            n = 1
            per_site = pd.Series(opt["install_person_hours"] / len(scope_sites), index=scope_sites)
        add(f"{option_id} {opt['option_name']}", n, opt["setup_usd"] * n, opt["annual_usd"] * n, per_site.to_dict(), f"per {unit.lower()}")

    if "O1" in deployed or "O2" in deployed:
        o2 = solutions.loc["O2"]
        # Conservative allocation: O2 install hours land on the sites that actually use the platform (O1 sites).
        o2_sites = monitored_sites or scope_sites
        share = o2["install_person_hours"] / len(o2_sites)
        add("O2 Data integration and alert platform (prerequisite for O1)", 1, o2["setup_usd"], o2["annual_usd"], {s: share for s in o2_sites}, f"once per organization; install hours split across {', '.join(o2_sites)}")
    if prereq_sites or "O6" in deployed:
        o6 = solutions.loc["O6"]
        o6_sites = sorted(set(prereq_sites) | set(sites_for.get("O6", [])))
        training = {s: sites.loc[s, "technicians"] * sites.loc[s, "training_hours_per_person"] for s in o6_sites}
        add("O6 Digital training (prerequisite)", len(o6_sites), o6["setup_usd"] * len(o6_sites), o6["annual_usd"] * len(o6_sites), training, "technicians x training hours, once per site")
    if prereq_sites:
        add("Site data cleanup (prerequisite)", len(prereq_sites), float(sites.loc[prereq_sites, "cleanup_setup_usd"].sum()), 0.0, note="Assets.cleanup_setup_usd per site")
    edge_sites = [s for s in monitored_sites if sites.loc[s, "network_uptime_pct"] < EDGE_UPTIME_THRESHOLD]
    if edge_sites:
        add("Edge buffering (prerequisite, uptime < 97%)", len(edge_sites), float(sites.loc[edge_sites, "edge_setup_usd"].sum()), float(sites.loc[edge_sites, "edge_annual_usd"].sum()), note=", ".join(edge_sites))

    hse_site = data.hse["asset_id"].map(site_of)  # site derived from the asset, as in the HSE gate
    open_hse = data.hse[(data.hse["action_status"] == "Open") & hse_site.isin(scope_sites)].assign(site_id=hse_site)
    if not open_hse.empty:
        add(
            "Open HSE corrective actions at in-scope sites",
            len(open_hse),
            float(open_hse["action_setup_usd"].sum()),
            float(open_hse["action_annual_usd"].sum()),
            open_hse.groupby("site_id")["action_person_hours"].sum().to_dict(),
            "required before or alongside rollout; severity-5 items gate the pilot",
        )

    resources = pd.DataFrame({"site_id": scope_sites, "required_hours": hours.values})
    resources["available_hours"] = resources["site_id"].map(sites["available_project_hours"])
    resources["shortfall_hours"] = (resources["required_hours"] - resources["available_hours"]).clip(lower=0)
    shortfall = resources["shortfall_hours"].sum()
    if shortfall > 0:
        add("Additional implementation help (assumption)", round(shortfall, 1), shortfall * plan.extra_help_rate_usd_hr, 0.0, note=f"shortfall hours x ${plan.extra_help_rate_usd_hr:g}/h")
    return pd.DataFrame(lines), resources
