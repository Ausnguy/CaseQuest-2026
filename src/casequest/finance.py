"""Monthly cash-flow view of a plan: payback, multi-year net, NPV, benefit/cost.

The ReadMe does not require ROI or payback, so these are supporting views built strictly from case inputs:
- costs come from options.model_plan (Solutions, Assets and HSE sheets)
- the benefit is modeled avoided contribution margin (ReadMe contribution formula), not cash
- timing follows roadmap waves
The discount rate and the price shift are assumptions, configurable and labeled.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from casequest.roadmap import Wave

MONTHS_PER_YEAR = 12


@dataclass
class FinanceResult:
    monthly: pd.DataFrame
    payback_month: int | None
    yearly: pd.DataFrame
    npv: float
    benefit_cost_ratio: float


def site_economics(plan_result, data, price_shift_usd_bbl: float = 0.0) -> pd.DataFrame:
    """Steady-state annual avoided hours and contribution per site, plus each site's O4 setup/annual cost."""
    ev = plan_result.events
    margin = ev["margin_usd_bbl"] + price_shift_usd_bbl
    contribution = ev["avoided_bbl"] * (1 - ev["recoverable_fraction"]) * margin
    per_site = pd.DataFrame(
        {
            "avoided_hours": ev.groupby("site_id")["avoided_hours"].sum(),
            "contribution_usd": contribution.groupby(ev["site_id"]).sum(),
        }
    )
    return per_site


def cash_flows(
    site_annual_contribution: pd.Series,
    waves: list[Wave],
    site_setup_usd: float,
    site_annual_usd: float,
    shared_upfront_usd: float,
    shared_annual_usd: float,
    months: int = 36,
    annual_discount_rate: float = 0.10,
) -> FinanceResult:
    """Month 0 = approval. Shared costs (HSE backlog) are paid in month 1 and run from month 1.

    Each site pays its setup in its go-live month (month 1 at the earliest); benefits and site annual costs start the
    month after.
    """
    go_live = {site: wave.go_live_month for wave in waves for site in wave.sites}
    rows = []
    for m in range(1, months + 1):
        benefit = sum(site_annual_contribution.get(s, 0.0) / MONTHS_PER_YEAR for s, g in go_live.items() if m > g)
        setup = sum(site_setup_usd for g in go_live.values() if m == max(g, 1)) + (shared_upfront_usd if m == 1 else 0.0)
        running = shared_annual_usd / MONTHS_PER_YEAR + sum(site_annual_usd / MONTHS_PER_YEAR for g in go_live.values() if m > g)
        rows.append({"month": m, "benefit_usd": benefit, "upfront_usd": setup, "annual_cost_usd": running})
    monthly = pd.DataFrame(rows)
    monthly["net_usd"] = monthly["benefit_usd"] - monthly["upfront_usd"] - monthly["annual_cost_usd"]
    monthly["cumulative_net_usd"] = monthly["net_usd"].cumsum()
    positive = monthly.loc[monthly["cumulative_net_usd"] >= 0, "month"]
    # Payback = first month after which the cumulative stays non-negative.
    payback = None
    for m in positive:
        if (monthly.loc[monthly["month"] >= m, "cumulative_net_usd"] >= 0).all():
            payback = int(m)
            break
    monthly["year"] = (monthly["month"] - 1) // MONTHS_PER_YEAR + 1
    yearly = monthly.groupby("year")[["benefit_usd", "upfront_usd", "annual_cost_usd", "net_usd"]].sum()
    yearly["cumulative_net_usd"] = yearly["net_usd"].cumsum()
    monthly_rate = (1 + annual_discount_rate) ** (1 / MONTHS_PER_YEAR) - 1
    npv = float((monthly["net_usd"] / (1 + monthly_rate) ** monthly["month"]).sum())
    total_cost = monthly["upfront_usd"].sum() + monthly["annual_cost_usd"].sum()
    bcr = float(monthly["benefit_usd"].sum() / total_cost) if total_cost else float("inf")
    return FinanceResult(monthly=monthly, payback_month=payback, yearly=yearly.reset_index(), npv=npv, benefit_cost_ratio=bcr)
