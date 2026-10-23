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

SCENARIO_YEAR = 2025
NO_STANDALONE_REDUCTION = "No standalone reduction"

# Allowed labels per categorical column. Case/spacing variants are mapped to these; anything else
# stops the build, because safety logic (e.g. the HSE gate) depends on exact labels.
CATEGORIES = {
    "Assets": {
        "asset_type": ["Transfer pump", "Lift pump", "Compressor"],
        "criticality": ["High", "Medium", "Low"],
    },
    "Events": {
        "event_type": ["Unplanned", "Planned"],
        "cause": ["Bearing wear", "Seal leak", "Electrical trip", "Process upset", "Unknown", "Scheduled service"],
        "work_type": ["Corrective", "Preventive"],
        "cost_status": ["Complete", "Parts invoice pending"],
    },
    "Readings": {
        "operating_state": ["Running", "Stopped"],
        "quality": ["Valid", "Suspect", "Missing"],
        "inspection_note": ["Routine inspection complete", "Operator noticed abnormal noise"],
    },
    "HSE": {
        "action_status": ["Open", "Closed"],
        "outcome": ["Control observation", "Near miss", "Contained spill"],
        "hazard": [
            "H2S monitoring",
            "Energy isolation / LOTO",
            "Pressurized line / line of fire",
            "Tank vapor exposure",
            "Hydrocarbon containment",
            "Lifting / dropped objects",
        ],
    },
    "Solutions": {
        "billing_unit": ["Asset", "Site", "Organization"],
    },
}
