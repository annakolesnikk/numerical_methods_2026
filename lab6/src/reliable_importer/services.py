import logging
from collections.abc import Collection, Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from reliable_importer.exceptions import RecordValidationError
from reliable_importer.models import Employee
from reliable_importer.readers import read_csv_rows
from reliable_importer.validators import parse_employee

logger = logging.getLogger(__name__)


@dataclass
class ImportStatistics:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    filtered: int = 0


def import_employees(
    path: Path,
    *,
    allowed_departments: Collection[str],
    skip_invalid: bool,
    statistics: ImportStatistics,
) -> Iterator[Employee]:
    for line_number, row in read_csv_rows(path):
        statistics.total += 1

        try:
            employee = parse_employee(
                row,
                line_number=line_number,
                allowed_departments=allowed_departments,
            )
        except RecordValidationError as error:
            statistics.invalid += 1
            # Only line, field and message are logged - never the row itself.
            logger.warning(
                "Invalid record at line %s (field '%s'): %s",
                error.line_number,
                error.field,
                error,
            )
            if skip_invalid:
                continue
            raise

        statistics.valid += 1
        yield employee


def filter_by_salary(
    employees: Iterable[Employee],
    minimum_salary: float,
    statistics: ImportStatistics,
) -> Iterator[Employee]:
    for employee in employees:
        if employee.salary >= minimum_salary:
            yield employee
        else:
            statistics.filtered += 1
            logger.info(
                "Employee %s skipped: salary below configured minimum",
                employee.employee_id,
            )