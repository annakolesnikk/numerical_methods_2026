import json
from collections.abc import Iterator
from pathlib import Path

import pytest

from reliable_importer.exceptions import DataExportError, DataImportError
from reliable_importer.exporters import export_employees_json
from reliable_importer.models import Employee
from reliable_importer.readers import read_csv_rows
from reliable_importer.utils import logged_operation

ANNA = Employee(1, "Anna Kolesnik", "Sales Manager", "Sales", 42000.0)
OLEH = Employee(2, "Oleh Ivanenko", "Backend Developer", "IT", 65000.0)


def test_export_writes_json_array(tmp_path: Path) -> None:
    output = tmp_path / "employees.json"

    count = export_employees_json([ANNA, OLEH], output)

    assert count == 2
    assert json.loads(output.read_text(encoding="utf-8")) == [
        ANNA.to_dict(),
        OLEH.to_dict(),
    ]


def test_export_empty_collection(tmp_path: Path) -> None:
    output = tmp_path / "employees.json"

    assert export_employees_json([], output) == 0
    assert json.loads(output.read_text(encoding="utf-8")) == []


def test_export_creates_missing_directory(tmp_path: Path) -> None:
    output = tmp_path / "new" / "dir" / "employees.json"

    export_employees_json([ANNA], output)

    assert output.exists()


def failing_employees() -> Iterator[Employee]:
    yield ANNA
    raise OSError("Disk is full")


def test_failed_export_keeps_previous_output(tmp_path: Path) -> None:
    output = tmp_path / "employees.json"
    output.write_text("old valid data", encoding="utf-8")

    with pytest.raises(DataExportError) as exc_info:
        export_employees_json(failing_employees(), output)

    assert output.read_text(encoding="utf-8") == "old valid data"
    assert not (tmp_path / "employees.json.tmp").exists()
    assert isinstance(exc_info.value.__cause__, OSError)


def test_reader_streams_rows_with_line_numbers(csv_factory) -> None:
    path = csv_factory("1,Anna Kolesnik,Manager,Sales,42000\n2,Oleh Ivanenko,Dev,IT,65000\n")

    rows = read_csv_rows(path)

    assert next(rows)[0] == 2
    line_number, row = next(rows)
    assert line_number == 3
    assert row["name"] == "Oleh Ivanenko"


def test_reader_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(DataImportError, match="Cannot read") as exc_info:
        list(read_csv_rows(tmp_path / "missing.csv"))

    assert isinstance(exc_info.value.__cause__, FileNotFoundError)


def test_reader_missing_columns_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("employee_id,name\n1,Anna\n", encoding="utf-8")

    with pytest.raises(DataImportError, match="Missing CSV columns: department, position, salary"):
        list(read_csv_rows(path))


def test_logged_operation_logs_success(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("INFO")

    with logged_operation("Export"):
        pass

    assert "Export started" in caplog.text
    assert "Export finished" in caplog.text


def test_logged_operation_logs_and_reraises_failure(caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(RuntimeError):
        with logged_operation("Export"):
            raise RuntimeError("boom")

    assert "Export failed" in caplog.text


def test_reader_malformed_csv_raises(tmp_path: Path) -> None:
    path = tmp_path / "huge.csv"
    path.write_text(
        "employee_id,name,position,department,salary\n"
        f'1,"{"x" * 200_000}",Dev,IT,1000\n',
        encoding="utf-8",
    )

    with pytest.raises(DataImportError, match="Malformed CSV") as exc_info:
        list(read_csv_rows(path))

    assert exc_info.value.__cause__ is not None    