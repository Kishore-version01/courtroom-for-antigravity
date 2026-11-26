"""Automated schema integrity, contract, and CLI validation tests (Phase 2)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
from typing import Any, Dict

from jsonschema import Draft202012Validator
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from court_engine import initialize_paths, load_configuration, main  # noqa: E402
from schema_validator import (  # noqa: E402
    BALLOT_SCHEMA_NAME,
    DOSSIER_SCHEMA_NAME,
    SchemaValidationError,
    clear_schema_cache,
    get_schema_version,
    load_json_payload,
    load_schema,
    validate_ballot,
    validate_dossier,
)


FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


def _valid_ballot_base() -> Dict[str, Any]:
    return copy.deepcopy(load_json_payload(FIXTURES_DIR / "valid_ballot.json"))


def _valid_dossier_base() -> Dict[str, Any]:
    return copy.deepcopy(load_json_payload(FIXTURES_DIR / "valid_dossier.json"))


# ---------------------------------------------------------------------------
# Schema Integrity Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("schema_name", [BALLOT_SCHEMA_NAME, DOSSIER_SCHEMA_NAME])
def test_schema_files_discoverable_and_valid_draft_2020_12(schema_name: str) -> None:
    paths = initialize_paths(load_configuration())
    schema_path = paths.schemas / schema_name
    assert schema_path.is_file()

    parsed = json.loads(schema_path.read_text(encoding="utf-8"))
    assert parsed["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert isinstance(parsed["version"], str) and parsed["version"] == "1.0.0"
    assert isinstance(parsed["required"], list) and len(parsed["required"]) > 0

    Draft202012Validator.check_schema(parsed)

    loaded = load_schema(schema_name)
    assert loaded == parsed
    assert get_schema_version(schema_name) == "1.0.0"


def test_schema_caching_reuses_loaded_object() -> None:
    clear_schema_cache()
    first = load_schema(BALLOT_SCHEMA_NAME)
    second = load_schema(BALLOT_SCHEMA_NAME)
    assert first is second


# ---------------------------------------------------------------------------
# Ballot Contract Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("vote", ["GUILTY", "NOT_GUILTY", "ABSTAIN"])
def test_ballot_valid_votes(vote: str) -> None:
    ballot = _valid_ballot_base()
    ballot["vote"] = vote
    validate_ballot(ballot)


@pytest.mark.parametrize("confidence", [0, 100])
def test_ballot_confidence_boundaries(confidence: int) -> None:
    ballot = _valid_ballot_base()
    ballot["confidence"] = confidence
    validate_ballot(ballot)


def test_ballot_empty_arrays_and_empty_dissent_allowed() -> None:
    ballot = {
        "vote": "ABSTAIN",
        "confidence": 50,
        "critical_objections": [],
        "concessions": [],
        "dissent": "",
    }
    validate_ballot(ballot)


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("confidence", -1),
        ("confidence", 101),
        ("confidence", 85.5),
        ("confidence", True),
        ("vote", "NOT GUILTY"),
        ("vote", "guilty"),
        ("vote", "APPROVE"),
        ("critical_objections", "not-a-list"),
        ("critical_objections", [123]),
        ("concessions", "not-a-list"),
        ("concessions", [456]),
        ("dissent", ["not-a-string"]),
        ("dissent", 42),
    ],
)
def test_ballot_invalid_field_values(field: str, bad_value: Any) -> None:
    ballot = _valid_ballot_base()
    ballot[field] = bad_value
    with pytest.raises(SchemaValidationError) as exc_info:
        validate_ballot(ballot)
    assert any(field in err for err in exc_info.value.errors)


@pytest.mark.parametrize(
    "missing_field",
    ["vote", "confidence", "critical_objections", "concessions", "dissent"],
)
def test_ballot_missing_required_field(missing_field: str) -> None:
    ballot = _valid_ballot_base()
    del ballot[missing_field]
    with pytest.raises(SchemaValidationError):
        validate_ballot(ballot)


def test_ballot_rejects_extra_fields() -> None:
    ballot = _valid_ballot_base()
    ballot["juror_id"] = "juror_sre"
    with pytest.raises(SchemaValidationError, match="Additional properties"):
        validate_ballot(ballot)


def test_ballot_fixtures() -> None:
    validate_ballot(load_json_payload(FIXTURES_DIR / "valid_ballot.json"))
    with pytest.raises(SchemaValidationError):
        validate_ballot(load_json_payload(FIXTURES_DIR / "invalid_ballot.json"))


# ---------------------------------------------------------------------------
# Dossier Contract Tests
# ---------------------------------------------------------------------------


def test_dossier_valid_fixture() -> None:
    validate_dossier(_valid_dossier_base())


@pytest.mark.parametrize(
    "missing_top_field",
    [
        "schema_version",
        "case",
        "prosecution",
        "defence",
        "evidence",
        "constraints",
        "assumptions",
        "context",
    ],
)
def test_dossier_missing_required_top_field(missing_top_field: str) -> None:
    dossier = _valid_dossier_base()
    del dossier[missing_top_field]
    with pytest.raises(SchemaValidationError):
        validate_dossier(dossier)


@pytest.mark.parametrize("missing_case_field", ["case_id", "title", "proposal"])
def test_dossier_missing_required_case_field(missing_case_field: str) -> None:
    dossier = _valid_dossier_base()
    del dossier["case"][missing_case_field]
    with pytest.raises(SchemaValidationError):
        validate_dossier(dossier)


def test_dossier_invalid_evidence_structure() -> None:
    dossier = _valid_dossier_base()
    dossier["evidence"] = [{"title": "Only a title"}]
    with pytest.raises(SchemaValidationError, match="evidence"):
        validate_dossier(dossier)


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("evidence", "none"),
        ("constraints", "none"),
        ("assumptions", {}),
        ("context", 123),
        ("schema_version", "2.0"),
        ("schema_version", "2.0.0"),
    ],
)
def test_dossier_invalid_types_and_version(field: str, bad_value: Any) -> None:
    dossier = _valid_dossier_base()
    dossier[field] = bad_value
    with pytest.raises(SchemaValidationError):
        validate_dossier(dossier)


@pytest.mark.parametrize(
    "bad_timestamp",
    ["not-a-timestamp", "2026-11-26", "2026-11-26T13:00:00"],
)
def test_dossier_invalid_created_at_datetime(bad_timestamp: str) -> None:
    dossier = _valid_dossier_base()
    dossier["case"]["created_at"] = bad_timestamp
    with pytest.raises(SchemaValidationError, match="created_at"):
        validate_dossier(dossier)


def test_dossier_rejects_extra_fields() -> None:
    dossier = _valid_dossier_base()
    dossier["unexpected"] = "nope"
    with pytest.raises(SchemaValidationError, match="Additional properties"):
        validate_dossier(dossier)


def test_dossier_invalid_fixture() -> None:
    with pytest.raises(SchemaValidationError):
        validate_dossier(load_json_payload(FIXTURES_DIR / "invalid_dossier.json"))


# ---------------------------------------------------------------------------
# CLI Validation Tests
# ---------------------------------------------------------------------------


def test_cli_validate_ballot_pass_and_fail(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--validate-ballot", str(FIXTURES_DIR / "valid_ballot.json")]) == 0
    out_pass = capsys.readouterr().out
    assert "Ballot Validation: PASS" in out_pass
    assert "Schema Version: 1.0.0" in out_pass

    assert main(["--validate-ballot", str(FIXTURES_DIR / "invalid_ballot.json")]) == 1
    err_fail = capsys.readouterr().err
    assert "Ballot Validation: FAIL" in err_fail
    assert "Errors:" in err_fail


def test_cli_validate_dossier_pass_and_fail(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--validate-dossier", str(FIXTURES_DIR / "valid_dossier.json")]) == 0
    out_pass = capsys.readouterr().out
    assert "Dossier Validation: PASS" in out_pass
    assert "Schema Version: 1.0.0" in out_pass

    assert main(["--validate-dossier", str(FIXTURES_DIR / "invalid_dossier.json")]) == 1
    err_fail = capsys.readouterr().err
    assert "Dossier Validation: FAIL" in err_fail
    assert "Errors:" in err_fail
