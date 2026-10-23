"""Integration tests against the real workbook."""

import hashlib

import pytest

from casequest.clean import clean_all
from casequest.config import RAW_WORKBOOK, RAW_WORKBOOK_SHA256
from casequest.validate import run_checks


@pytest.fixture(scope="module")
def data():
    return clean_all()


def test_raw_workbook_is_untouched(data):
    assert hashlib.sha256(RAW_WORKBOOK.read_bytes()).hexdigest() == RAW_WORKBOOK_SHA256


def test_clean_row_counts(data):
    counts = {name: len(df) for name, df in data.tables().items()}
    assert counts == {
        "assets": 18, "sites": 6, "events": 385, "production": 216,
        "readings": 6570, "solutions": 6, "hse": 36,
    }


def test_every_reconciliation_check_passes(data):
    failed = [f"{c.name}: {c.detail}" for c in run_checks(data) if not c.passed]
    assert failed == []


def test_reconciliation_detects_a_broken_production_row(data):
    data.production.loc[0, "gross_deferred_bbl"] += 50
    try:
        failed = {c.name for c in run_checks(data) if not c.passed}
    finally:
        data.production.loc[0, "gross_deferred_bbl"] -= 50
    assert "Production: gross_deferred = sum of event lost_oil (planned + unplanned)" in failed


def test_event_counts_by_type(data):
    assert data.events["event_type"].value_counts().to_dict() == {"Unplanned": 313, "Planned": 72}


def test_hse_gate_flags_three_sites(data):
    blocked = data.hse.loc[data.hse["blocks_pilot"], "site_id"]
    assert sorted(blocked.unique()) == ["S02", "S04", "S06"]
    assert len(blocked) == 6
