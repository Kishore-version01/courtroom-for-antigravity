"""Foundational tests for Phase 1 of the Courtroom for Antigravity engine."""

from __future__ import annotations

import logging
from pathlib import Path
import sys
import uuid

import pytest

# Ensure repository root is importable regardless of pytest invocation path.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import court_engine  # noqa: E402
from court_engine import (  # noqa: E402
    ConfigurationError,
    CourtError,
    InitializationError,
    ProjectStructureError,
    RuntimeDirectoryError,
    initialize_logging,
    initialize_paths,
    initialize_runtime_directories,
    load_configuration,
    main,
    resolve_project_root,
    validate_foundation,
)


# ---------------------------------------------------------------------------
# Path Tests
# ---------------------------------------------------------------------------


def test_project_root_resolves_correctly() -> None:
    root = resolve_project_root()
    assert root == REPO_ROOT
    assert (root / "court_engine.py").is_file()


def test_paths_independent_of_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    config = load_configuration({})
    paths = initialize_paths(config)

    assert paths.root == REPO_ROOT
    assert paths.scripts == REPO_ROOT / "scripts"
    assert paths.schemas == REPO_ROOT / "schemas"
    assert paths.references == REPO_ROOT / "references"
    assert paths.templates == REPO_ROOT / "references" / "templates"
    assert paths.tests == REPO_ROOT / "tests"
    assert paths.runtime == (REPO_ROOT / ".court").resolve()
    assert paths.cases == (REPO_ROOT / ".court" / "cases").resolve()


def test_missing_project_structure_raises_error(tmp_path: Path) -> None:
    config = load_configuration({})
    with pytest.raises(ProjectStructureError, match="Required project directory"):
        initialize_paths(config, root=tmp_path)


# ---------------------------------------------------------------------------
# Configuration Tests
# ---------------------------------------------------------------------------


def test_default_configuration_loads() -> None:
    config = load_configuration({})
    assert config.project_name == "Courtroom for Antigravity"
    assert config.project_version == "0.1.0"
    assert config.runtime_dir == ".court"
    assert config.log_level == "INFO"
    assert config.default_trial_mode == "full"


def test_environment_overrides_work() -> None:
    env = {
        "COURT_PROJECT_NAME": "Custom Court",
        "COURT_PROJECT_VERSION": "0.2.0",
        "COURT_RUNTIME_DIR": ".custom_court",
        "COURT_LOG_LEVEL": "debug",
        "COURT_DEFAULT_TRIAL_MODE": "SPEED",
    }
    config = load_configuration(env)
    assert config.project_name == "Custom Court"
    assert config.project_version == "0.2.0"
    assert config.runtime_dir == ".custom_court"
    assert config.log_level == "DEBUG"
    assert config.default_trial_mode == "speed"


@pytest.mark.parametrize(
    ("overrides", "expected_fragment"),
    [
        ({"COURT_LOG_LEVEL": "VERBOSE"}, "Invalid log_level"),
        ({"COURT_RUNTIME_DIR": "   "}, "runtime_dir"),
        ({"COURT_PROJECT_NAME": ""}, "project_name"),
        ({"COURT_DEFAULT_TRIAL_MODE": "turbo"}, "Invalid default_trial_mode"),
    ],
)
def test_invalid_configuration_raises_error(
    overrides: dict[str, str], expected_fragment: str
) -> None:
    with pytest.raises(ConfigurationError, match=expected_fragment):
        load_configuration(overrides)


# ---------------------------------------------------------------------------
# Logging Tests
# ---------------------------------------------------------------------------


def _unique_logger_name() -> str:
    return f"court_engine_test_{uuid.uuid4().hex}"


def test_logging_initializes_and_avoids_duplicate_handlers() -> None:
    logger_name = _unique_logger_name()
    config = load_configuration({"COURT_LOG_LEVEL": "INFO"})

    logger1 = initialize_logging(config, logger_name=logger_name)
    handler_count_first = len(logger1.handlers)

    logger2 = initialize_logging(config, logger_name=logger_name)
    assert logger1 is logger2
    assert len(logger2.handlers) == handler_count_first == 1
    assert logger2.propagate is False


def test_logging_respects_configured_levels(capsys: pytest.CaptureFixture[str]) -> None:
    logger_name = _unique_logger_name()
    config = load_configuration({"COURT_LOG_LEVEL": "WARNING"})
    logger = initialize_logging(config, logger_name=logger_name)

    assert logger.level == logging.WARNING
    assert logger.handlers[0].level == logging.WARNING
    assert not logger.isEnabledFor(logging.INFO)
    assert logger.isEnabledFor(logging.WARNING)

    logger.info("suppressed info message")
    logger.warning("visible warning message")
    captured = capsys.readouterr()
    assert "suppressed info message" not in captured.err
    assert "visible warning message" in captured.err


# ---------------------------------------------------------------------------
# Runtime Directory Tests
# ---------------------------------------------------------------------------


def _make_fake_project(base: Path) -> Path:
    for rel in ("scripts", "schemas", "references/templates", "tests"):
        (base / rel).mkdir(parents=True, exist_ok=True)
    return base


def test_runtime_directories_created_and_idempotent(tmp_path: Path) -> None:
    project_root = _make_fake_project(tmp_path)
    config = load_configuration({})
    paths = initialize_paths(config, root=project_root)

    initialize_runtime_directories(paths)
    assert paths.runtime.is_dir()
    assert paths.cases.is_dir()

    # Preserve existing case data across repeated initializations
    existing_case_dir = paths.cases / "2026-11-26_sample-case"
    existing_case_dir.mkdir(parents=True, exist_ok=True)
    existing_file = existing_case_dir / "dossier.json"
    existing_file.write_text('{"case": "preserved"}', encoding="utf-8")

    initialize_runtime_directories(paths)
    assert existing_file.is_file()
    assert existing_file.read_text(encoding="utf-8") == '{"case": "preserved"}'


def test_runtime_file_collision_raises_error(tmp_path: Path) -> None:
    project_root = _make_fake_project(tmp_path)
    (project_root / ".court").write_text("not a directory", encoding="utf-8")
    config = load_configuration({})
    paths = initialize_paths(config, root=project_root)

    with pytest.raises(RuntimeDirectoryError, match="not a directory"):
        initialize_runtime_directories(paths)


# ---------------------------------------------------------------------------
# Exception & CLI Tests
# ---------------------------------------------------------------------------


def test_exception_hierarchy_and_messages() -> None:
    assert issubclass(ConfigurationError, CourtError)
    assert issubclass(ProjectStructureError, CourtError)
    assert issubclass(RuntimeDirectoryError, CourtError)
    assert issubclass(InitializationError, CourtError)

    err = ConfigurationError("Invalid setting detected")
    assert "Invalid setting detected" in str(err)


def test_validate_foundation_checks_state(tmp_path: Path) -> None:
    project_root = _make_fake_project(tmp_path)
    config = load_configuration({})
    paths = initialize_paths(config, root=project_root)
    logger = initialize_logging(config, logger_name=_unique_logger_name())

    with pytest.raises(InitializationError, match="not properly initialized"):
        validate_foundation(config, paths, logger)

    initialize_runtime_directories(paths)
    validate_foundation(config, paths, logger)


def test_cli_main_succeeds_and_handles_errors(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main()
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "COURTROOM FOR ANTIGRAVITY" in captured.out
    assert "Phase 1 Status: READY" in captured.out
    assert "Phase 2 Status: NOT IMPLEMENTED" in captured.out

    monkeypatch.setenv("COURT_LOG_LEVEL", "INVALID")
    err_code = court_engine.main()
    err_captured = capsys.readouterr()
    assert err_code == 1
    assert "[ERROR]" in err_captured.err
