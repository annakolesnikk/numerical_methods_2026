import pytest

from reliable_importer.exceptions import RecordValidationError
from reliable_importer.validators import parse_employee

DEPARTMENTS = {"Sales", "IT", "Finance", "HR"}


def make_row(**overrides: str) -> dict[str, str]:
    row = {
        "employee_id": "1",
        "name": "Anna Kolesnik",
        "position": "Sales Manager",
        "department": "Sales",
        "salary": "42000",
    }
    row.update(overrides)
    return row


def test_valid_row_creates_employee() -> None:
    employee = parse_employee(make_row(), line_number=2, allowed_departments=DEPARTMENTS)

    assert employee.employee_id == 1
    assert employee.name == "Anna Kolesnik"
    assert employee.department == "Sales"
    assert employee.salary == pytest.approx(42_000)


def test_values_are_stripped() -> None:
    employee = parse_employee(
        make_row(name="  Anna Kolesnik  ", department=" IT "),
        line_number=2,
        allowed_departments=DEPARTMENTS,
    )

    assert employee.name == "Anna Kolesnik"
    assert employee.department == "IT"


@pytest.mark.parametrize(
    "salary",
    [
        pytest.param("0", id="minimum"),
        pytest.param("0.01", id="just-above-minimum"),
        pytest.param("999999.99", id="large"),
    ],
)
def test_boundary_valid_salary(salary: str) -> None:
    employee = parse_employee(
        make_row(salary=salary), line_number=2, allowed_departments=DEPARTMENTS
    )

    assert employee.salary == pytest.approx(float(salary))


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        pytest.param({"employee_id": "abc"}, "employee_id", id="id-not-number"),
        pytest.param({"employee_id": "0"}, "employee_id", id="id-zero"),
        pytest.param({"employee_id": "-5"}, "employee_id", id="id-negative"),
        pytest.param({"name": ""}, "name", id="name-empty"),
        pytest.param({"name": "Anna"}, "name", id="name-one-word"),
        pytest.param({"position": "  "}, "position", id="position-blank"),
        pytest.param({"department": "Legal"}, "department", id="department-not-allowed"),
        pytest.param({"salary": "-0.01"}, "salary", id="salary-just-below-zero"),
        pytest.param({"salary": "abc"}, "salary", id="salary-not-number"),
        pytest.param({"salary": ""}, "salary", id="salary-empty"),
        pytest.param({"salary": "nan"}, "salary", id="salary-nan"),
        pytest.param({"salary": "inf"}, "salary", id="salary-infinity"),
    ],
)
def test_invalid_row_raises_record_validation_error(
    overrides: dict[str, str],
    field: str,
) -> None:
    with pytest.raises(RecordValidationError) as exc_info:
        parse_employee(make_row(**overrides), line_number=7, allowed_departments=DEPARTMENTS)

    assert exc_info.value.field == field
    assert exc_info.value.line_number == 7


def test_missing_column_raises_validation_error() -> None:
    row = make_row()
    del row["salary"]

    with pytest.raises(RecordValidationError) as exc_info:
        parse_employee(row, line_number=3, allowed_departments=DEPARTMENTS)

    assert exc_info.value.field == "salary"


def test_salary_error_keeps_original_cause() -> None:
    with pytest.raises(RecordValidationError) as exc_info:
        parse_employee(make_row(salary="wrong"), line_number=2, allowed_departments=DEPARTMENTS)

    assert isinstance(exc_info.value.__cause__, ValueError)


def test_salary_value_is_not_in_error_message() -> None:
    with pytest.raises(RecordValidationError) as exc_info:
        parse_employee(make_row(salary="-1234"), line_number=2, allowed_departments=DEPARTMENTS)

    assert "1234" not in str(exc_info.value)