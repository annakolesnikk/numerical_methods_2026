import json

import pytest

from reliable_importer.exceptions import RecordValidationError
from reliable_importer.exporters import export_employees_json
from reliable_importer.services import (
    ImportStatistics,
    filter_by_salary,
    import_employees,
)

pytestmark = pytest.mark.integration

DEPARTMENTS = {"Sales", "IT", "Finance", "HR"}

ROWS = (
    "1,Anna Kolesnik,Sales Manager,Sales,42000\n"
    "2,Oleh Ivanenko,Backend Developer,IT,65000\n"
    "3,Olena Kovalenko,Sales Representative,Sales,28000\n"
    "4,,Tester,IT,40000\n"
    "abc,Petro Novak,Designer,IT,47000\n"
    "6,Kateryna Moroz,HR Manager,HR,45000\n"
)


def test_tolerant_csv_to_json_pipeline(csv_factory, tmp_path) -> None:
    source = csv_factory(ROWS)
    output = tmp_path / "out" / "employees.json"
    statistics = ImportStatistics()

    employees = import_employees(
        source,
        allowed_departments=DEPARTMENTS,
        skip_invalid=True,
        statistics=statistics,
    )
    exported = export_employees_json(
        filter_by_salary(employees, 30_000, statistics), output
    )

    data = json.loads(output.read_text(encoding="utf-8"))
    assert exported == 3
    assert [item["employee_id"] for item in data] == [1, 2, 6]
    assert (statistics.total, statistics.valid, statistics.invalid, statistics.filtered) == (
        6, 4, 2, 1,
    )


def test_strict_pipeline_stops_and_keeps_old_output(csv_factory, tmp_path) -> None:
    source = csv_factory(ROWS)
    output = tmp_path / "employees.json"
    output.write_text("[]\n", encoding="utf-8")
    statistics = ImportStatistics()

    with pytest.raises(RecordValidationError) as exc_info:
        export_employees_json(
            import_employees(
                source,
                allowed_departments=DEPARTMENTS,
                skip_invalid=False,
                statistics=statistics,
            ),
            output,
        )

    assert exc_info.value.line_number == 5
    assert statistics.invalid == 1
    assert output.read_text(encoding="utf-8") == "[]\n"
    assert not (tmp_path / "employees.json.tmp").exists()


def test_malformed_csv_records_are_logged(csv_factory, caplog) -> None:
    source = csv_factory("1,Anna Kolesnik,Sales Manager,Sales\n2,Oleh Ivanenko,Dev,IT,-500\n")
    statistics = ImportStatistics()

    result = list(
        import_employees(
            source,
            allowed_departments=DEPARTMENTS,
            skip_invalid=True,
            statistics=statistics,
        )
    )

    assert result == []
    assert statistics.invalid == 2
    assert "line 2 (field 'salary')" in caplog.text
    assert "-500" not in caplog.text