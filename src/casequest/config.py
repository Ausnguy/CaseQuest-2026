"""Project paths and fixed scenario constants."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_WORKBOOK = REPO_ROOT / "Dataset-Rules" / "CaseQuest2026Dataset.xlsx"
RAW_WORKBOOK_SHA256 = "b4d32ee1935619eec5a7729428e525eb74c44f2d5cd04a0f7e13fe4cd84533b8"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
DOCS_DIR = REPO_ROOT / "docs"

DATA_SHEETS = ["Assets", "Events", "Production", "Readings", "Solutions", "HSE"]

STAGES = ["detect_hours", "dispatch_hours", "parts_wait_hours", "repair_hours", "restart_hours"]

# Site-level fields repeat on every Assets row of a site (ReadMe "Site resources").
SITE_FIELDS = [
    "site_name",
    "network_uptime_pct",
    "technicians",
    "spare_fill_pct",
    "training_hours_per_person",
    "edge_setup_usd",
    "edge_annual_usd",
    "cleanup_setup_usd",
    "available_project_hours",
]

# Readings arriving more than this long after observation count as delayed.
DELAYED_INGEST_HOURS = 1.0
