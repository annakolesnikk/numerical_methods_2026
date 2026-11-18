from pathlib import Path
from typing import Any

import yaml

from reliable_importer.exceptions import ConfigurationError
from reliable_importer.models import AppConfig, LoggingConfig, ProcessingConfig

LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def load_config(path: Path) -> AppConfig:
    try:
        with path.open("r", encoding="utf-8") as file:
            raw: Any = yaml.safe_load(file)
    except FileNotFoundError as error:
        raise ConfigurationError(
            f"Configuration file not found: {path}"
        ) from error
    except yaml.YAMLError as error:
        raise ConfigurationError("Invalid YAML configuration") from error

    try:
        departments = raw["processing"]["allowed_departments"]
        if not isinstance(departments, list):
            raise TypeError("allowed_departments must be a list")

        config = AppConfig(
            input_path=Path(raw["input"]["path"]),
            output_path=Path(raw["output"]["path"]),
            processing=ProcessingConfig(
                minimum_salary=float(raw["processing"]["minimum_salary"]),
                skip_invalid=bool(raw["processing"]["skip_invalid"]),
                allowed_departments=frozenset(
                    str(name).strip() for name in departments
                ),
            ),
            logging=LoggingConfig(
                level=str(raw["logging"]["level"]).upper(),
                path=Path(raw["logging"]["path"]),
            ),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ConfigurationError(
            "Configuration structure is invalid"
        ) from error

    validate_config(config)
    return config


def validate_config(config: AppConfig) -> None:
    if config.processing.minimum_salary < 0:
        raise ConfigurationError("minimum_salary must be non-negative")

    if not config.processing.allowed_departments:
        raise ConfigurationError("allowed_departments must not be empty")

    if config.logging.level not in LOG_LEVELS:
        raise ConfigurationError(
            f"Unknown logging level: {config.logging.level}"
        )

    if not config.input_path.is_file():
        raise ConfigurationError(
            f"Input file not found: {config.input_path}"
        )