import csv
from collections.abc import Iterator
from pathlib import Path

from reliable_importer.exceptions import DataImportError

REQUIRED_COLUMNS = {"employee_id", "name", "position", "department", "salary"}


def read_csv_rows(path: Path) -> Iterator[tuple[int, dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise DataImportError(
                    f"Missing CSV columns: {', '.join(sorted(missing))}"
                )

            for line_number, row in enumerate(reader, start=2):
                yield line_number, row
    except OSError as error:
        raise DataImportError(f"Cannot read input file: {path}") from error
    except csv.Error as error:
        raise DataImportError(f"Malformed CSV file: {path}") from error