import math
from collections.abc import Collection

from reliable_importer.exceptions import RecordValidationError
from reliable_importer.models import Employee


def parse_employee(
    row: dict[str, str],
    *,
    line_number: int,
    allowed_departments: Collection[str],
) -> Employee:
    try:
        employee_id = int(row["employee_id"])
    except (KeyError, TypeError, ValueError) as error:
        raise RecordValidationError(
            "Employee ID must be an integer",
            line_number=line_number,
            field="employee_id",
        ) from error

    if employee_id <= 0:
        raise RecordValidationError(
            "Employee ID must be positive",
            line_number=line_number,
            field="employee_id",
        )

    name = (row.get("name") or "").strip()
    if len(name.split()) < 2:
        raise RecordValidationError(
            "Employee full name is empty or incomplete",
            line_number=line_number,
            field="name",
        )

    position = (row.get("position") or "").strip()
    if not position:
        raise RecordValidationError(
            "Position is empty",
            line_number=line_number,
            field="position",
        )

    department = (row.get("department") or "").strip()
    if department not in allowed_departments:
        raise RecordValidationError(
            f"Department '{department}' is not allowed",
            line_number=line_number,
            field="department",
        )

    # Salary is confidential: error messages never contain its value.
    try:
        salary = float(row["salary"])
    except (KeyError, TypeError, ValueError) as error:
        raise RecordValidationError(
            "Salary must be numeric",
            line_number=line_number,
            field="salary",
        ) from error

    if not math.isfinite(salary):
        raise RecordValidationError(
            "Salary must be a finite number",
            line_number=line_number,
            field="salary",
        )

    if salary < 0:
        raise RecordValidationError(
            "Salary must be non-negative",
            line_number=line_number,
            field="salary",
        )

    return Employee(
        employee_id=employee_id,
        name=name,
        position=position,
        department=department,
        salary=salary,
    )