"""Core foundation for the Courtroom for Antigravity engine.

Phase 1 establishes configuration management, cross-platform project path
resolution, centralized logging, custom exceptions, and idempotent runtime
directory initialization.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import os
from pathlib import Path
import sys
import tempfile
from typing import Mapping, Optional


VALID_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
VALID_TRIAL_MODES = frozenset({"full", "speed"})
DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class CourtError(Exception):
    """Base exception for all Courtroom engine errors."""


class ConfigurationError(CourtError):
    """Raised when engine configuration is missing or invalid."""


class ProjectStructureError(CourtError):
    """Raised when required project directories cannot be resolved."""


class RuntimeDirectoryError(CourtError):
    """Raised when runtime directory creation or verification fails."""


class InitializationError(CourtError):
    """Raised when foundation validation or startup fails."""


@dataclass(frozen=True)
class CourtConfig:
    """Centralized configuration for the Courtroom engine."""

    project_name: str = "Courtroom for Antigravity"
    project_version: str = "0.1.0"
    runtime_dir: str = ".court"
    log_level: str = "INFO"
    log_format: str = DEFAULT_LOG_FORMAT
    log_date_format: str = DEFAULT_LOG_DATE_FORMAT
    default_trial_mode: str = "full"

    def validate(self) -> None:
        """Validate configuration values and raise ConfigurationError if invalid."""
        if not self.project_name or not self.project_name.strip():
            raise ConfigurationError("project_name must be a non-empty string.")
        if not self.project_version or not self.project_version.strip():
            raise ConfigurationError("project_version must be a non-empty string.")
        if not self.runtime_dir or not self.runtime_dir.strip():
            raise ConfigurationError("runtime_dir must be a non-empty path string.")
        if self.log_level.upper() not in VALID_LOG_LEVELS:
            allowed = ", ".join(sorted(VALID_LOG_LEVELS))
            raise ConfigurationError(
                f"Invalid log_level '{self.log_level}'. Expected one of: {allowed}."
            )
        if not self.log_format or not self.log_format.strip():
            raise ConfigurationError("log_format must be a non-empty format string.")
        if not self.log_date_format or not self.log_date_format.strip():
            raise ConfigurationError("log_date_format must be a non-empty date format string.")
        if self.default_trial_mode not in VALID_TRIAL_MODES:
            allowed_modes = ", ".join(sorted(VALID_TRIAL_MODES))
            raise ConfigurationError(
                f"Invalid default_trial_mode '{self.default_trial_mode}'. "
                f"Expected one of: {allowed_modes}."
            )


@dataclass(frozen=True)
class ProjectPaths:
    """Centralized cross-platform paths for the Courtroom project."""

    root: Path
    scripts: Path
    schemas: Path
    references: Path
    templates: Path
    tests: Path
    runtime: Path
    cases: Path


def load_configuration(env: Optional[Mapping[str, str]] = None) -> CourtConfig:
    """Load and validate engine configuration with optional environment overrides."""
    source = os.environ if env is None else env

    raw_level = source.get("COURT_LOG_LEVEL", "INFO")
    raw_mode = source.get("COURT_DEFAULT_TRIAL_MODE", "full")

    config = CourtConfig(
        project_name=source.get("COURT_PROJECT_NAME", "Courtroom for Antigravity"),
        project_version=source.get("COURT_PROJECT_VERSION", "0.1.0"),
        runtime_dir=source.get("COURT_RUNTIME_DIR", ".court"),
        log_level=raw_level.strip().upper() if isinstance(raw_level, str) else str(raw_level),
        log_format=source.get("COURT_LOG_FORMAT", DEFAULT_LOG_FORMAT),
        log_date_format=source.get("COURT_LOG_DATE_FORMAT", DEFAULT_LOG_DATE_FORMAT),
        default_trial_mode=raw_mode.strip().lower() if isinstance(raw_mode, str) else str(raw_mode),
    )
    config.validate()
    return config


def resolve_project_root(root: Optional[Path] = None) -> Path:
    """Resolve the repository root independently of the current working directory."""
    candidate = Path(__file__).resolve().parent if root is None else Path(root).resolve()
    if not candidate.exists() or not candidate.is_dir():
        raise ProjectStructureError(f"Project root does not exist or is not a directory: {candidate}")
    return candidate


def initialize_paths(config: CourtConfig, root: Optional[Path] = None) -> ProjectPaths:
    """Build and verify centralized project paths."""
    project_root = resolve_project_root(root)

    runtime_candidate = Path(config.runtime_dir)
    runtime_path = (
        runtime_candidate
        if runtime_candidate.is_absolute()
        else (project_root / runtime_candidate).resolve()
    )

    paths = ProjectPaths(
        root=project_root,
        scripts=project_root / "scripts",
        schemas=project_root / "schemas",
        references=project_root / "references",
        templates=project_root / "references" / "templates",
        tests=project_root / "tests",
        runtime=runtime_path,
        cases=runtime_path / "cases",
    )

    required_dirs = (
        ("scripts", paths.scripts),
        ("schemas", paths.schemas),
        ("references", paths.references),
        ("templates", paths.templates),
        ("tests", paths.tests),
    )
    for label, directory in required_dirs:
        if not directory.exists() or not directory.is_dir():
            raise ProjectStructureError(
                f"Required project directory '{label}' is missing: {directory}"
            )

    return paths


def initialize_logging(
    config: CourtConfig,
    logger_name: str = "court_engine",
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """Configure centralized logging without duplicating handlers."""
    config.validate()
    level = getattr(logging, config.log_level)

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(fmt=config.log_format, datefmt=config.log_date_format)

    stream_handler = next(
        (
            handler
            for handler in logger.handlers
            if isinstance(handler, logging.StreamHandler)
            and not isinstance(handler, logging.FileHandler)
        ),
        None,
    )
    if stream_handler is None:
        stream_handler = logging.StreamHandler()
        logger.addHandler(stream_handler)

    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    if log_file is not None:
        resolved_log_file = Path(log_file).resolve()
        file_handler = next(
            (
                handler
                for handler in logger.handlers
                if isinstance(handler, logging.FileHandler)
                and Path(handler.baseFilename).resolve() == resolved_log_file
            ),
            None,
        )
        if file_handler is None:
            try:
                resolved_log_file.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(resolved_log_file, encoding="utf-8")
            except OSError as exc:
                raise InitializationError(
                    f"Failed to initialize log file at {resolved_log_file}: {exc}"
                ) from exc
            logger.addHandler(file_handler)

        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

    return logger


def initialize_runtime_directories(paths: ProjectPaths) -> None:
    """Safely and idempotently create runtime directories and verify write access."""
    for target in (paths.runtime, paths.cases):
        if target.exists() and not target.is_dir():
            raise RuntimeDirectoryError(
                f"Runtime path exists but is not a directory: {target}"
            )
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RuntimeDirectoryError(
                f"Unable to create runtime directory '{target}': {exc}"
            ) from exc

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            prefix=".court_write_check_",
            dir=paths.cases,
            delete=True,
            encoding="utf-8",
        ) as probe:
            probe.write("ok")
            probe.flush()
    except OSError as exc:
        raise RuntimeDirectoryError(
            f"Runtime directory is not writable '{paths.cases}': {exc}"
        ) from exc


def validate_foundation(
    config: CourtConfig,
    paths: ProjectPaths,
    logger: logging.Logger,
) -> None:
    """Verify that all foundational components are initialized and consistent."""
    config.validate()
    if not paths.runtime.is_dir() or not paths.cases.is_dir():
        raise InitializationError(
            f"Runtime directories are not properly initialized under {paths.runtime}"
        )
    if not logger.handlers:
        raise InitializationError("Logging system has no configured handlers.")


def display_status(config: CourtConfig) -> None:
    """Print clean initialization status for Phase 1."""
    banner = "=" * 50
    print(banner)
    print(f" {config.project_name.upper()}")
    print(banner)
    print()
    print("[INFO] Project configuration loaded")
    print("[INFO] Project paths resolved")
    print("[INFO] Logging initialized")
    print("[INFO] Runtime directories verified")
    print()
    print("Court Engine Foundation Initialized Successfully.")
    print()
    print("Phase 1 Status: READY")
    print("Phase 2 Status: NOT IMPLEMENTED")


def main() -> int:
    """Run Phase 1 foundation initialization sequence."""
    try:
        config = load_configuration()
        paths = initialize_paths(config)
        logger = initialize_logging(config)
        logger.info("Court Engine initialized")
        initialize_runtime_directories(paths)
        logger.info("Runtime directories verified")
        validate_foundation(config, paths, logger)
        display_status(config)
        return 0
    except CourtError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
