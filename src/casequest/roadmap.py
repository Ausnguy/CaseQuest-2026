"""Gate-first rollout of the recommendation and its first-year benefit.

Assumptions (all configurable, none come from the case data):
- A site's benefit starts the month after it goes live and accrues evenly through the year.
- Sites blocked by the HSE gate go live only after the site HSE supervisor verifies closure
  plus the option's lead time.
Steady-state annual benefit per site comes from options.model_plan.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from casequest.clean import CleanData

MONTHS = 12


@dataclass(frozen=True)
class Wave:
    name: str
    sites: tuple[str, ...]
    go_live_month: int  # benefits start after this month (0 = live from day one)


def gate_first_waves(
    data: CleanData,
    lead_months: int = 1,
    hse_verified_month: int = 3,
    pilot_site: str = "S05",
) -> list[Wave]:
    """Pilot an unblocked site first, then the other unblocked sites, then blocked sites after verified closure.

    Blocked sites are ordered by downtime (largest first) and staggered one month apart because each needs its
    own inventory audit and stocking.
    """
    sites = data.sites.set_index("site_id")
    blocked = sites.index[sites["pilot_blocked"]].tolist()
    unblocked = [s for s in sites.index if s not in blocked]
    if pilot_site not in unblocked:
        raise ValueError(f"Pilot site {pilot_site} is blocked by the HSE gate or unknown; choose one of {unblocked}")
    downtime = data.events[data.events["event_type"] == "Unplanned"].groupby("site_id")["stopped_hours"].sum()
    first_blocked, *other_blocked = sorted(blocked, key=lambda s: -downtime.get(s, 0))
    return [
        Wave("Pilot", (pilot_site,), lead_months),
        Wave("Unblocked sites", tuple(s for s in unblocked if s != pilot_site), lead_months + 1),
        Wave("Largest blocked site (after HSE verification)", (first_blocked,), hse_verified_month + lead_months),
        Wave("Remaining blocked sites (after HSE verification)", tuple(other_blocked), hse_verified_month + lead_months + 1),
    ]


def first_year(site_annual_hours: pd.Series, waves: list[Wave]) -> pd.DataFrame:
    """Year-one share of each site's steady-state hours, from the month its wave goes live."""
    rows = []
    for wave in waves:
        for site in wave.sites:
            live_months = max(MONTHS - wave.go_live_month, 0)
            steady = float(site_annual_hours.get(site, 0.0))
            rows.append(
                {
                    "wave": wave.name,
                    "site_id": site,
                    "go_live_month": wave.go_live_month,
                    "steady_state_hours": steady,
                    "year1_hours": steady * live_months / MONTHS,
                }
            )
    out = pd.DataFrame(rows)
    missing = set(site_annual_hours.index) - set(out["site_id"])
    if missing:
        raise ValueError(f"Sites with benefit but no wave: {sorted(missing)}")
    return out
