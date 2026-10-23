"""Turn the raw CaseQuest workbook into clean, analysis-ready tables.

Every change is recorded in a CleaningLog so the audit trail can be published.
The raw workbook is only ever read, never written.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from casequest.config import DATA_SHEETS, DELAYED_INGEST_HOURS, RAW_WORKBOOK, SITE_FIELDS, STAGES


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
    """'22 bbl/hr' or 22 -> 22.0"""
    match = re.search(r"\d+(?:\.\d+)?", str(value))
    if not match:
        raise DataQualityError(f"Unparseable capacity: {value!r}")
    return float(match.group())


def parse_temperature_c(value) -> float:
    """Numbers are already Celsius; strings ending in 'F' are converted to Celsius."""
    if pd.isna(value):
        return np.nan
    text = str(value).strip()
    if text.upper().endswith("F"):
        return round((float(text[:-1].strip()) - 32) * 5 / 9, 2)
    return float(text)


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
            "ReadMe 'Raw quality': some IDs contain whitespace/lowercase. Mapped to canonical A### form.",
            examples,
        )
    return df.assign(**{column: normalized})


def _strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for column in out.columns:
        if out[column].dtype == object or pd.api.types.is_string_dtype(out[column]):
            out[column] = out[column].map(lambda v: v.strip() if isinstance(v, str) else v)
    return out


# ---------------------------------------------------------------------------
# Table-level cleaning
# ---------------------------------------------------------------------------


def clean_assets(raw: pd.DataFrame, log: CleaningLog) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = _normalize_id_column(_strip_strings(raw), "asset_id", "Assets", log)

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

    per_site = df.groupby("site_id")[SITE_FIELDS].nunique()
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
    df = _strip_strings(raw)
    df = _normalize_id_column(df, "asset_id", "Events", log)
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
            "ReadMe 'Raw quality': recover durations from five stages. Dictionary: stopped_hours = sum of stages = end_utc - start_utc.",
            df.loc[missing, "event_id"].tolist(),
        )
    df["stopped_hours"] = stage_total.round(2)

    pending = df["parts_usd"].isna()
    log.add(
        "Events",
        "Keep pending parts invoices as unknown (not zero)",
        pending.sum(),
        "ReadMe 'Maintenance': pending parts invoices stay unknown, not zero. "
        "known_cost_usd excludes them and is flagged cost_complete = False.",
        df.loc[pending, "event_id"].tolist(),
    )
    df["known_cost_usd"] = df["labor_hours"] * df["labor_rate_usd_hr"] + df["parts_usd"].fillna(0) + df["contractor_usd"]
    df["cost_complete"] = ~pending
    df["month"] = df["start_utc"].dt.to_period("M").dt.to_timestamp()
    return df


def clean_production(raw: pd.DataFrame, assets: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    df = _normalize_id_column(_strip_strings(raw), "asset_id", "Production", log)
    df = drop_verified_duplicates(df, ["asset_id", "month"], "Production", log)

    capacity = df["asset_id"].map(assets.set_index("asset_id")["modeled_capacity_bbl_hr"])
    missing = df["potential_oil_bbl"].isna()
    if missing.any():
        log.add(
            "Production",
            "Recover missing potential_oil_bbl = calendar_hours x capacity",
            missing.sum(),
            "ReadMe 'Raw quality' and 'Production': potential = calendar_hours * capacity.",
            [f"{a} {m:%Y-%m}" for a, m in zip(df.loc[missing, "asset_id"], df.loc[missing, "month"])],
        )
    df.loc[missing, "potential_oil_bbl"] = (df.loc[missing, "calendar_hours"] * capacity[missing]).round(2)
    return df


def clean_readings(raw: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    df = _strip_strings(raw)
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
        "for every row. Original asset_tag retained.",
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

    df["ingest_lag_hours"] = (df["received_utc"] - df["observed_utc"]).dt.total_seconds() / 3600
    df["delayed_ingest"] = df["ingest_lag_hours"] > DELAYED_INGEST_HOURS
    log.add(
        "Readings",
        f"Flag delayed ingestion (> {DELAYED_INGEST_HOURS:g} h after observation)",
        df["delayed_ingest"].sum(),
        "Dictionary: a delayed timestamp is not a corruption to overwrite. Timestamps unchanged; flag added so "
        "prototype logic can use only data received by decision time.",
    )
    return df


def clean_hse(raw: pd.DataFrame, assets: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    df = _strip_strings(raw)
    df = _normalize_id_column(df, "asset_id", "HSE", log)
    df = drop_verified_duplicates(df, "hse_id", "HSE", log)

    for column in ["due_date", "closed_date", "status_as_of"]:
        df[column] = pd.to_datetime(df[column])

    is_open = df["action_status"] == "Open"
    df["is_overdue"] = is_open & (df["due_date"] < df["status_as_of"])
    df["blocks_pilot"] = is_open & (df["potential_severity"] == 5)
    df["net_spill_bbl"] = df["spilled_oil_bbl"] - df["recovered_spill_bbl"]
    log.add(
        "HSE",
        "Derive is_overdue, blocks_pilot, net_spill_bbl",
        len(df),
        "ReadMe 'HSE decision gate' and 'HSE measures': open severity-5 actions block the site pilot; overdue is "
        "evaluated against status_as_of (2026-10-01); spill measure is spilled minus recovered.",
    )
    return df


def clean_solutions(raw: pd.DataFrame, log: CleaningLog) -> pd.DataFrame:
    df = _strip_strings(raw)
    blank = df["eligible_causes"].isna()
    df["eligible_causes"] = df["eligible_causes"].fillna("None")
    log.add(
        "Solutions",
        "Label blank eligible_causes as 'None'",
        blank.sum(),
        "O2 and O6 have no standalone modeled reduction (benefit_rule); blank means no eligible causes.",
        df.loc[blank, "option_id"].tolist(),
    )
    return df


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
    hse = clean_hse(raw["HSE"], assets, log)
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
