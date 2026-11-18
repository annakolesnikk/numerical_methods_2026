import logging
import os
import sys
from pathlib import Path

from reliable_importer.config import load_config
from reliable_importer.exceptions import ApplicationError
from reliable_importer.exporters import export_employees_json
from reliable_importer.logging_config import configure_logging
from reliable_importer.services import (
    ImportStatistics,
    filter_by_salary,
    import_employees,
)
from reliable_importer.utils import logged_operation

logger = logging.getLogger(__name__)

CONFIG_ENV = "RELIABLE_IMPORTER_CONFIG"


def resolve_config_path(argv: list[str]) -> Path:
    if len(argv) > 1:
        return Path(argv[1])
    return Path(os.getenv(CONFIG_ENV, "config.yaml"))


def main() -> None:
    config_path = resolve_config_path(sys.argv)

    try:
        config = load_config(config_path)
        configure_logging(config.logging.level, config.logging.path)

        statistics = ImportStatistics()

        with logged_operation("Employee import/export"):
            employees = import_employees(
                config.input_path,
                allowed_departments=config.processing.allowed_departments,
                skip_invalid=config.processing.skip_invalid,
                statistics=statistics,
            )
            selected = filter_by_salary(
                employees,
                config.processing.minimum_salary,
                statistics,
            )
            exported = export_employees_json(selected, config.output_path)

        logger.info(
            "Total=%s, valid=%s, invalid=%s, filtered=%s, exported=%s",
            statistics.total,
            statistics.valid,
            statistics.invalid,
            statistics.filtered,
            exported,
        )
    except ApplicationError as error:
        logger.error("Application error: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()