"""Turn the raw CaseQuest workbook into clean, analysis-ready tables.

Every change is recorded in a CleaningLog so the audit trail can be published.
The raw workbook is only ever read, never written.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from casequest.config import CATEGORIES, DATA_SHEETS, DELAYED_INGEST_HOURS, HSE_SNAPSHOT_DATE, NO_STANDALONE_REDUCTION, RAW_WORKBOOK, SITE_FIELDS, STAGES


class DataQualityError(ValueError):
    """Raised when raw data breaks an assumption that cleaning cannot safely resolve."""


@dataclass
class LogEntry:
    table: str
    rule: str
    rows_affected: int
    rationale: str
    examples: list[str] = field(default_factory=list)


@dataclass
class CleaningLog:
    entries: list[LogEntry] = field(default_factory=list)

    def add(self, table: str, rule: str, rows_affected: int, rationale: str, examples=None) -> None:
        self.entries.append(LogEntry(table, rule, int(rows_affected), rationale, list(examples or [])[:10]))


@dataclass
class CleanData:
    assets: pd.DataFrame
    sites: pd.DataFrame
    events: pd.DataFrame
    production: pd.DataFrame
    readings: pd.DataFrame
    solutions: pd.DataFrame
    hse: pd.DataFrame
    raw_row_counts: dict[str, int]
    log: CleaningLog

    def tables(self) -> dict[str, pd.DataFrame]:
        return {
            "assets": self.assets,
            "sites": self.sites,
            "events": self.events,
            "production": self.production,
            "readings": self.readings,
            "solutions": self.solutions,
            "hse": self.hse,
        }


# ---------------------------------------------------------------------------
# Reusable value-level rules
# ---------------------------------------------------------------------------

_ASSET_ID = re.compile(r"A?0*(\d+)")
_LEGACY_TAG = re.compile(r"LEG-0*(\d+)")
_CAPACITY = re.compile(r"(\d+(?:\.\d+)?)\s*(?:BBL/HR)?", re.IGNORECASE)
_TEMPERATURE = re.compile(r"(-?\d+(?:\.\d+)?)\s*(F)?", re.IGNORECASE)


def normalize_asset_id(value) -> str:
    """'a010', 'A09', 8, ' A001 ' -> 'A010', 'A009', 'A008', 'A001'."""
    text = str(value).strip().upper()
    match = _ASSET_ID.fullmatch(text)
    if not match:
        raise DataQualityError(f"Unrecognised asset identifier: {value!r}")
    return f"A{int(match.group(1)):03d}"


def resolve_reading_tag(tag) -> str:
    """Map a raw Readings tag (canonical or legacy LEG-nnn) to its asset_id."""
    text = str(tag).strip().upper()
    legacy = _LEGACY_TAG.fullmatch(text)
    if legacy:
        return f"A{int(legacy.group(1)):03d}"
    return normalize_asset_id(text)


def parse_capacity(value) -> float:
    """'22 bbl/hr' or 22 -> 22.0. Any other unit is rejected rather than silently read."""
    match = _CAPACITY.fullmatch(str(value).strip())
    if not match:
        raise DataQualityError(f"Unparseable capacity (expected bbl/hr): {value!r}")
    return float(match.group(1))


def parse_temperature_c(value) -> float:
    """Numbers are already Celsius; values suffixed 'F' are converted. Anything else is rejected."""
    if pd.isna(value):
        return np.nan
    match = _TEMPERATURE.fullmatch(str(value).strip())
    if not match:
        raise DataQualityError(f"Unparseable temperature: {value!r}")
    number = float(match.group(1))
    return round((number - 32) * 5 / 9, 2) if match.group(2) else number


def normalize_categories(df: pd.DataFrame, table: str, log: CleaningLog) -> pd.DataFrame:
    """Map case/spacing variants to canonical labels; raise on any value outside the allowed set.

    Safety-relevant logic (e.g. the HSE gate) compares exact labels, so an unexpected variant such
    as 'open' must never pass silently.
    """
    out = df.copy()
    for column, allowed in CATEGORIES.get(table, {}).items():
        if column not in out.columns:
            raise DataQualityError(f"{table}: expected column {column!r} is missing")
        lookup = {label.casefold(): label for label in allowed}
        present = out[column].dropna()
        canonical = present.map(lambda v: lookup.get(" ".join(str(v).split()).casefold()))
        unknown = present[canonical.isna()]
        if not unknown.empty:
            raise DataQualityError(f"{table}.{column}: unexpected values {sorted(map(str, unknown.unique()))[:10]}")
        changed = canonical != present
        if changed.any():
            log.add(
                table,
                f"Normalize {column} labels",
                changed.sum(),
                "Case/spacing variant mapped to its canonical category.",
                [f"{old!r} -> {new}" for old, new in zip(present[changed], canonical[changed])],
            )
        out.loc[present.index, column] = canonical
    return out


def drop_verified_duplicates(df: pd.DataFrame, key: str | list[str], table: str, log: CleaningLog) -> pd.DataFrame:
    """Remove repeated export rows, but only when every copy is identical.

    Two rows sharing a key but differing anywhere else are a conflict that needs a
    human decision, so that case raises instead of silently keeping one.
    """
    key_cols = [key] if isinstance(key, str) else key
    repeated = df[df.duplicated(key_cols, keep=False)]
    conflicting = repeated.drop_duplicates()
    conflicting = conflicting[conflicting.duplicated(key_cols, keep=False)]
    if not conflicting.empty:
        keys = conflicting[key_cols].drop_duplicates().astype(str).agg("/".join, axis=1).tolist()
        raise DataQualityError(f"{table}: conflicting rows share a key: {keys[:10]}")
    deduped = df.drop_duplicates()
    removed = len(df) - len(deduped)
    if removed:
        examples = repeated[key_cols].drop_duplicates().astype(str).agg("/".join, axis=1).tolist()
        log.add(
            table,
            "Remove verified export copies",
            removed,
            "ReadMe 'Keys': remove verified export copies. Every removed row was identical to a kept row in all columns.",
            examples,
        )
    return deduped.reset_index(drop=True)


def _normalize_id_column(df: pd.DataFrame, column: str, table: str, log: CleaningLog) -> pd.DataFrame:
    normalized = df[column].map(normalize_asset_id)
    changed = normalized != df[column].astype(str)
    if changed.any():
        examples = [f"{old!r} -> {new}" for old, new in zip(df.loc[changed, column], normalized[changed])]
        log.add(
            table,
            f"Normalize {column}",
            changed.sum(),
            "ReadMe 'Raw quality': some IDs are lowercase, unpadded or numeric. Mapped to canonical A### form.",
            examples,
        )
    return df.assign(**{column: normalized})


def _strip_strings(df: pd.DataFrame, table: str, log: CleaningLog) -> pd.DataFrame:
    out = df.copy()
    changed = 0
    for column in out.columns:
        if out[column].dtype == object or pd.api.types.is_string_dtype(out[column]):
            stripped = out[column].map(lambda v: v.strip() if isinstance(v, str) else v)
            changed += int((stripped.fillna("\0") != out[column].fillna("\0")).sum())
            out[column] = stripped
    log.add(table, "Trim leading/trailing whitespace in text cells", changed, "ReadMe 'Raw quality': some IDs contain whitespace. Logged even when zero.")
    return out


# ---------------------------------------------------------------------------
# Table-level cleaning
# ---------------------------------------------------------------------------


def clean_assets(raw: pd.DataFrame, log: CleaningLog) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = _normalize_id_column(_strip_strings(raw, "Assets", log), "asset_id", "Assets", log)
    df = normalize_categories(df, "Assets", log)

    capacity = df["modeled_capacity_bbl_hr"].map(parse_capacity)
    had_units = df["modeled_capacity_bbl_hr"].map(lambda v: isinstance(v, str))
    if had_units.any():
        log.add(
            "Assets",
            "Strip units from modeled_capacity_bbl_hr",
            had_units.sum(),
            "ReadMe 'Raw quality': capacities include units. Kept the numeric bbl/hr value.",
            [f"{a}: {v!r} -> {c:g}" for a, v, c in zip(df.loc[had_units, "asset_id"], df.loc[had_units, "modeled_capacity_bbl_hr"], capacity[had_units])],
        )
    df["modeled_capacity_bbl_hr"] = capacity

    per_site = df.groupby("site_id")[SITE_FIELDS].nunique(dropna=False)
    inconsistent = per_site[(per_site > 1).any(axis=1)]
    if not inconsistent.empty:
        raise DataQualityError(f"Site fields differ within a site: {inconsistent.index.tolist()}")
    sites = df[["site_id", *SITE_FIELDS]].drop_duplicates("site_id").reset_index(drop=True)
    log.add(
        "Assets",
        "Split site-level fields into a Sites table",
        len(df) - len(sites),
        "ReadMe 'Site resources': site fields repeat on three Assets rows; read once per site. "
        "Verified identical within each site before collapsing.",
    )
    assets = df.drop(columns=[c for c in SITE_FIELDS if c != "site_name"])
    return assets, sites


def clean_events(raw: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    df = _strip_strings(raw, "Events", log)
    df = _normalize_id_column(df, "asset_id", "Events", log)
    df = normalize_categories(df, "Events", log)
    df = drop_verified_duplicates(df, "event_id", "Events", log)

    stage_total = df[STAGES].sum(axis=1)
    disagree = df["stopped_hours"].notna() & ((df["stopped_hours"] - stage_total).abs() > 0.01)
    if disagree.any():
        raise DataQualityError(f"stopped_hours disagrees with stage sum for {df.loc[disagree, 'event_id'].tolist()[:10]}")
    missing = df["stopped_hours"].isna()
    if missing.any():
        log.add(
            "Events",
            "Recover missing stopped_hours from the five stages",
            missing.sum(),
            "ReadMe 'Raw quality': recover durations from five stages. Dictionary: stopped_hours = sum of stages = end_utc - start_utc. "
            "Only blank rows are filled; flagged stopped_hours_recovered.",
            df.loc[missing, "event_id"].tolist(),
        )
    df.loc[missing, "stopped_hours"] = stage_total[missing].round(2)
    df["stopped_hours_recovered"] = missing

    pending = df["parts_usd"].isna()
    log.add(
        "Events",
        "Keep pending parts invoices as unknown (not zero)",
        pending.sum(),
        "ReadMe 'Maintenance': pending parts invoices stay unknown, not zero. known_cost_usd is blank for these events; "
        "known_cost_lower_bound_usd counts only the known parts (labor + contractor).",
        df.loc[pending, "event_id"].tolist(),
    )
    labor_and_contractor = df["labor_hours"] * df["labor_rate_usd_hr"] + df["contractor_usd"]
    df["known_cost_usd"] = labor_and_contractor + df["parts_usd"]
    df["known_cost_lower_bound_usd"] = labor_and_contractor + df["parts_usd"].fillna(0)
    df["cost_complete"] = ~pending
    df["month"] = df["start_utc"].dt.to_period("M").dt.to_timestamp()
    return df


def clean_production(raw: pd.DataFrame, assets: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    df = _normalize_id_column(_strip_strings(raw, "Production", log), "asset_id", "Production", log)
    df = drop_verified_duplicates(df, ["asset_id", "month"], "Production", log)

    capacity = df["asset_id"].map(assets.set_index("asset_id")["modeled_capacity_bbl_hr"])
    missing = df["potential_oil_bbl"].isna()
    if missing.any():
        log.add(
            "Production",
            "Recover missing potential_oil_bbl = calendar_hours x capacity",
            missing.sum(),
            "ReadMe 'Raw quality' and 'Production': potential = calendar_hours * capacity. Flagged potential_recovered.",
            [f"{a} {m:%Y-%m}" for a, m in zip(df.loc[missing, "asset_id"], df.loc[missing, "month"])],
        )
    df.loc[missing, "potential_oil_bbl"] = (df.loc[missing, "calendar_hours"] * capacity[missing]).round(2)
    df["potential_recovered"] = missing
    return df


def clean_readings(raw: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    df = _strip_strings(raw, "Readings", log)
    df = normalize_categories(df, "Readings", log)
    df = drop_verified_duplicates(df, "reading_id", "Readings", log)

    provided = df["asset_id"].map(normalize_asset_id)
    resolved = df["asset_tag"].map(resolve_reading_tag)
    mismatched = provided != resolved
    if mismatched.any():
        raise DataQualityError(f"Readings tag mapping disagrees for {df.loc[mismatched, 'reading_id'].tolist()[:10]}")
    legacy = df["asset_tag"].str.upper().str.startswith("LEG-")
    log.add(
        "Readings",
        "Map legacy LEG-nnn tags to asset_id",
        legacy.sum(),
        "ReadMe 'Sensor limitations': legacy raw tags remain. Verified LEG-nnn -> Annn agrees with the supplied asset_id "
        "(the only mapping aid; the workbook has no TagMap tab) for every row. Original asset_tag retained.",
    )
    df["asset_id"] = provided

    fahrenheit = df["temperature_c"].map(lambda v: isinstance(v, str) and v.strip().upper().endswith("F"))
    converted = df["temperature_c"].map(parse_temperature_c)
    if fahrenheit.any():
        log.add(
            "Readings",
            "Convert Fahrenheit temperatures to Celsius",
            fahrenheit.sum(),
            "ReadMe 'Raw quality': temperatures have explicit F suffix. C = (F - 32) x 5/9, rounded to 2 dp.",
            [f"{r}: {v!r} -> {c:.2f} C" for r, v, c in zip(df.loc[fahrenheit, "reading_id"], df.loc[fahrenheit, "temperature_c"], converted[fahrenheit])],
        )
    df["temperature_c"] = converted.astype(float)

    missing = df["vibration_mm_s"].isna() | df["temperature_c"].isna()
    log.add(
        "Readings",
        "Leave missing measurements as missing",
        missing.sum(),
        "ReadMe 'Sensor limitations': missing original measurements cannot be restored. No imputation.",
    )
    log.add(
        "Readings",
        "Keep Suspect rows, flagged",
        (df["quality"] == "Suspect").sum(),
        "Dictionary: Suspect is not a confirmed fault. Rows retained with their quality flag; analyses decide whether to use them.",
    )

    df["ingest_lag_hours"] = ((df["received_utc"] - df["observed_utc"]).dt.total_seconds() / 3600).round(4)
    df["delayed_ingest"] = df["ingest_lag_hours"] > DELAYED_INGEST_HOURS
    log.add(
        "Readings",
        f"Flag delayed ingestion (> {DELAYED_INGEST_HOURS:g} h after observation)",
        df["delayed_ingest"].sum(),
        "Dictionary: a delayed timestamp is not a corruption to overwrite. Timestamps unchanged; flag added so "
        "prototype logic can use only data received by decision time.",
    )
    return df


def _ordinal_band(series: pd.Series, column: str) -> pd.Series:
    """Coerce a 1-5 ordinal band to int (text '5' is fine); anything else stops the build."""
    numeric = pd.to_numeric(series.map(lambda v: v.strip() if isinstance(v, str) else (np.nan if isinstance(v, (bool, np.bool_)) else v)), errors="coerce")
    bad = numeric.isna() | ~numeric.isin([1, 2, 3, 4, 5])
    if bad.any():
        raise DataQualityError(f"HSE.{column}: expected an integer 1-5, got {sorted(map(repr, series[bad].unique()))[:10]}")
    return numeric.astype(int)


def clean_hse(raw: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    """HSE observations with the pilot gate. The gate fails closed: ambiguous inputs stop the build."""
    df = _strip_strings(raw, "HSE", log)
    df = _normalize_id_column(df, "asset_id", "HSE", log)
    df = normalize_categories(df, "HSE", log)
    df = drop_verified_duplicates(df, "hse_id", "HSE", log)

    blank_status = df["action_status"].isna()
    if blank_status.any():
        raise DataQualityError(f"HSE.action_status is blank for {df.loc[blank_status, 'hse_id'].tolist()}; the pilot gate cannot be evaluated")
    for column in ["potential_severity", "likelihood_band"]:
        df[column] = _ordinal_band(df[column], column)
    for column in ["due_date", "closed_date", "status_as_of"]:
        try:
            df[column] = pd.to_datetime(df[column], format="%Y-%m-%d")
        except (ValueError, TypeError) as err:
            raise DataQualityError(f"HSE.{column}: dates must be YYYY-MM-DD ({err})") from err
    if not (df["status_as_of"] == HSE_SNAPSHOT_DATE).all():
        raise DataQualityError(f"HSE.status_as_of must be {HSE_SNAPSHOT_DATE:%Y-%m-%d} for every row")
    if df["observed_utc"].isna().any():
        raise DataQualityError(f"HSE.observed_utc is blank for {df.loc[df['observed_utc'].isna(), 'hse_id'].tolist()}")
    if df["due_date"].isna().any():
        raise DataQualityError(f"HSE.due_date is blank for {df.loc[df['due_date'].isna(), 'hse_id'].tolist()}")
    dated = df["closed_date"].notna()
    out_of_range = dated & ((df["closed_date"] < df["observed_utc"].dt.normalize()) | (df["closed_date"] > df["status_as_of"]))
    if out_of_range.any():
        raise DataQualityError(f"HSE.closed_date must fall between observation and the {HSE_SNAPSHOT_DATE:%Y-%m-%d} snapshot: {df.loc[out_of_range, 'hse_id'].tolist()}")

    # Fail closed: an action counts as open unless it is marked Closed AND has a verified closure date on or
    # before the snapshot.
    is_open = (df["action_status"] != "Closed") | df["closed_date"].isna() | (df["closed_date"] > df["status_as_of"])
    critical = df["potential_severity"] == 5
    df["is_overdue"] = is_open & (df["due_date"] < df["status_as_of"])
    df["is_overdue_critical"] = df["is_overdue"] & critical
    df["blocks_pilot"] = is_open & critical
    df["net_spill_bbl"] = df["spilled_oil_bbl"] - df["recovered_spill_bbl"]
    log.add(
        "HSE",
        "Derive is_overdue, is_overdue_critical, blocks_pilot, net_spill_bbl",
        len(df),
        "ReadMe 'HSE decision gate' and 'HSE measures': open severity-5 actions block the site pilot; overdue is "
        "evaluated against status_as_of (2026-10-01); spill measure is spilled minus recovered.",
    )
    return df


def clean_solutions(raw: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    df = normalize_categories(_strip_strings(raw, "Solutions", log), "Solutions", log)
    blank = df["eligible_causes"].isna()
    df["eligible_causes"] = df["eligible_causes"].fillna(NO_STANDALONE_REDUCTION)
    log.add(
        "Solutions",
        f"Label blank eligible_causes as '{NO_STANDALONE_REDUCTION}'",
        blank.sum(),
        "O2 and O6 have no standalone modeled reduction (benefit_rule). An explicit token is used because pandas reads 'None' back as missing.",
        df.loc[blank, "option_id"].tolist(),
    )
    return df


def add_site_gate(sites: pd.DataFrame, hse: pd.DataFrame, assets: pd.DataFrame) -> pd.DataFrame:
    """Site-level HSE status: a site with any open severity-5 action cannot enter the pilot.

    The site is derived from the action's asset via Assets, so a mistyped HSE.site_id cannot unblock a site.
    """
    site_of_asset = hse["asset_id"].map(assets.set_index("asset_id")["site_id"])
    if site_of_asset.isna().any():
        raise DataQualityError(f"HSE rows reference unknown assets: {hse.loc[site_of_asset.isna(), 'hse_id'].tolist()}")
    blocking = hse[hse["blocks_pilot"]].groupby(site_of_asset[hse["blocks_pilot"]]).size()
    out = sites.copy()
    out["open_sev5_actions"] = out["site_id"].map(blocking).fillna(0).astype(int)
    out["pilot_blocked"] = out["open_sev5_actions"] > 0
    return out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def load_raw(path=RAW_WORKBOOK) -> dict[str, pd.DataFrame]:
    return pd.read_excel(path, sheet_name=DATA_SHEETS)


def clean_all(raw: dict[str, pd.DataFrame] | None = None) -> CleanData:
    raw = raw if raw is not None else load_raw()
    log = CleaningLog()
    assets, sites = clean_assets(raw["Assets"], log)
    events = clean_events(raw["Events"], log)
    events = events.merge(assets[["asset_id", "site_id"]], on="asset_id", how="left", validate="many_to_one")
    production = clean_production(raw["Production"], assets, log)
    readings = clean_readings(raw["Readings"], log)
    hse = clean_hse(raw["HSE"], log)
    sites = add_site_gate(sites, hse, assets)
    solutions = clean_solutions(raw["Solutions"], log)
    return CleanData(
        assets=assets,
        sites=sites,
        events=events,
        production=production,
        readings=readings,
        solutions=solutions,
        hse=hse,
        raw_row_counts={name: len(df) for name, df in raw.items()},
        log=log,
    )
