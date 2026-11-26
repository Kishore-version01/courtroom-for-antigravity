"""Schema loading and Draft 2020-12 validation utilities for Courtroom for Antigravity."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError

from court_engine import CourtError, initialize_paths, load_configuration


BALLOT_SCHEMA_NAME = "ballot_schema.json"
DOSSIER_SCHEMA_NAME = "dossier_schema.json"

_SCHEMA_CACHE: Dict[Tuple[Path, str], Dict[str, Any]] = {}

_FORMAT_CHECKER = FormatChecker()


@_FORMAT_CHECKER.checks("date-time", ValueError)
def _check_iso8601_datetime(value: object) -> bool:
    """Validate ISO 8601 / RFC 3339 date-time strings with explicit timezone."""
    if not isinstance(value, str):
        return True
    if "T" not in value and "t" not in value:
        raise ValueError("date-time must include 'T' separator between date and time.")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("date-time must include a timezone offset or 'Z'.")
    return True


class SchemaValidationError(CourtError):
    """Raised when a schema is invalid or a payload fails contract validation."""

    def __init__(self, message: str, errors: Optional[List[str]] = None) -> None:
        super().__init__(message)
        self.errors: List[str] = list(errors or [])


def clear_schema_cache() -> None:
    """Clear the in-memory schema cache."""
    _SCHEMA_CACHE.clear()


def _resolve_schemas_dir(schemas_dir: Optional[Path] = None) -> Path:
    """Resolve the schemas directory using Phase 1 centralized paths by default."""
    if schemas_dir is not None:
        return Path(schemas_dir).resolve()
    config = load_configuration()
    return initialize_paths(config).schemas


def _normalize_schema_filename(schema_name: str) -> str:
    """Normalize a schema identifier to its JSON filename."""
    return schema_name if schema_name.endswith(".json") else f"{schema_name}.json"


def load_schema(schema_name: str, schemas_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Load, integrity-check, and cache a JSON Schema from the schemas directory."""
    resolved_dir = _resolve_schemas_dir(schemas_dir)
    filename = _normalize_schema_filename(schema_name)
    cache_key = (resolved_dir, filename)

    if cache_key in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[cache_key]

    schema_path = resolved_dir / filename
    if not schema_path.is_file():
        raise SchemaValidationError(f"Schema file not found: {schema_path}")

    try:
        raw_text = schema_path.read_text(encoding="utf-8")
        schema = json.loads(raw_text)
    except (OSError, json.JSONDecodeError) as exc:
        raise SchemaValidationError(
            f"Failed to load schema '{filename}': {exc}"
        ) from exc

    if not isinstance(schema, dict):
        raise SchemaValidationError(
            f"Schema '{filename}' must be a JSON object, got {type(schema).__name__}."
        )

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise SchemaValidationError(
            f"Schema '{filename}' failed Draft 2020-12 integrity check: {exc.message}"
        ) from exc

    _SCHEMA_CACHE[cache_key] = schema
    return schema


def _format_error_path(error: ValidationError) -> str:
    """Format a jsonschema ValidationError path into a readable field locator."""
    if not error.path:
        return "<root>"
    parts: List[str] = []
    for segment in error.path:
        if isinstance(segment, int):
            if parts:
                parts[-1] = f"{parts[-1]}[{segment}]"
            else:
                parts.append(f"[{segment}]")
        else:
            parts.append(str(segment))
    return ".".join(parts)


def validate_data(
    data: Any,
    schema: Mapping[str, Any],
    label: str = "Data",
) -> None:
    """Validate an arbitrary Python payload against a Draft 2020-12 JSON schema."""
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise SchemaValidationError(
            f"Invalid schema provided for {label} validation: {exc.message}"
        ) from exc

    validator = Draft202012Validator(schema, format_checker=_FORMAT_CHECKER)
    raw_errors = sorted(
        validator.iter_errors(data),
        key=lambda err: ([str(p) for p in err.path], err.message),
    )

    if raw_errors:
        formatted = [
            f"{_format_error_path(err)}: {err.message}" for err in raw_errors
        ]
        summary = "; ".join(formatted)
        raise SchemaValidationError(
            f"{label} validation failed: {summary}",
            errors=formatted,
        )


def validate_ballot(ballot: Any, schemas_dir: Optional[Path] = None) -> None:
    """Validate a juror ballot payload against schemas/ballot_schema.json."""
    schema = load_schema(BALLOT_SCHEMA_NAME, schemas_dir=schemas_dir)
    validate_data(ballot, schema, label="Ballot")


def validate_dossier(dossier: Any, schemas_dir: Optional[Path] = None) -> None:
    """Validate a trial dossier payload against schemas/dossier_schema.json."""
    schema = load_schema(DOSSIER_SCHEMA_NAME, schemas_dir=schemas_dir)
    validate_data(dossier, schema, label="Dossier")


def load_json_payload(file_path: Path) -> Any:
    """Load and parse a JSON payload from disk."""
    target = Path(file_path)
    if not target.is_file():
        raise SchemaValidationError(f"JSON file not found: {target}")
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SchemaValidationError(
            f"Failed to parse JSON file '{target}': {exc}"
        ) from exc


def get_schema_version(schema_name: str, schemas_dir: Optional[Path] = None) -> str:
    """Return the declared semantic version of a schema."""
    schema = load_schema(schema_name, schemas_dir=schemas_dir)
    version = schema.get("version")
    if not isinstance(version, str) or not version.strip():
        raise SchemaValidationError(f"Schema '{schema_name}' is missing a valid 'version' field.")
    return version
