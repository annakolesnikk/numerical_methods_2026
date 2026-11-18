from dataclasses import FrozenInstanceError

import pytest

from domain_app.dto import EmployeePayload, employee_from_payload
from domain_app.models import (
    Department,
    Developer,
    Employee,
    Manager,
    PayrollRecord,
)
from domain_app.value_objects import Money


def test_employee_is_created_with_salary(accountant: Employee) -> None:
    assert accountant.salary == Money(38_000)
    assert accountant.department_name is None
    assert str(accountant) == "Iryna Petrenko (Accountant, no department)"


def test_change_salary_updates_value(accountant: Employee) -> None:
    accountant.change_salary(Money(40_000))

    assert accountant.salary.amount == pytest.approx(40_000)


def test_change_salary_with_other_currency_raises(accountant: Employee) -> None:
    with pytest.raises(ValueError, match="Currency mismatch"):
        accountant.change_salary(Money(1_000, "USD"))


def test_employee_with_negative_salary_cannot_be_created() -> None:
    with pytest.raises(ValueError):
        Employee(id=10, name="Bad Salary", position="Tester", _salary=Money(-1))


def test_manager_monthly_pay_includes_bonus(manager: Manager) -> None:
    assert manager.monthly_pay().amount == pytest.approx(50_000)
    assert "bonus: 8000.00 UAH" in manager.describe()


def test_developer_description_contains_level(developer: Developer) -> None:
    assert developer.monthly_pay() == developer.salary
    assert "level: Senior" in developer.describe()


def test_department_add_assigns_employee(
    it_department: Department,
    developer: Developer,
) -> None:
    it_department.add(developer)

    assert developer.department_name == "IT"
    assert len(it_department) == 1
    assert developer.id in it_department
    assert list(it_department) == [developer]


def test_department_rejects_duplicate_employee(
    it_department: Department,
    developer: Developer,
) -> None:
    it_department.add(developer)

    with pytest.raises(ValueError, match="already in department"):
        it_department.add(developer)


def test_employee_cannot_be_in_two_departments(
    it_department: Department,
    developer: Developer,
) -> None:
    sales = Department(id=1, name="Sales")
    sales.add(developer)

    with pytest.raises(ValueError, match="already belongs"):
        it_department.add(developer)

    assert developer.id not in it_department
    assert developer.department_name == "Sales"


def test_empty_department_has_zero_total_salary(it_department: Department) -> None:
    assert len(it_department) == 0
    assert it_department.total_salary == Money(0)


def test_department_total_salary(
    it_department: Department,
    employee_factory,
) -> None:
    it_department.add(employee_factory(employee_id=1, salary=10_000.10))
    it_department.add(employee_factory(employee_id=2, salary=20_000.20))

    assert it_department.total_salary.amount == pytest.approx(30_000.30)


def test_payroll_record_is_immutable(accountant: Employee) -> None:
    record = PayrollRecord(
        id=1, employee=accountant, period="2026-11", amount=Money(38_000)
    )

    assert str(record) == "2026-11 Iryna Petrenko: 38000.00 UAH"
    with pytest.raises(FrozenInstanceError):
        record.period = "2026-12"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("role", "expected_type"),
    [
        ("manager", Manager),
        ("developer", Developer),
        ("employee", Employee),
    ],
)
def test_employee_from_payload_creates_correct_type(
    role: str,
    expected_type: type,
) -> None:
    payload: EmployeePayload = {
        "id": 5,
        "name": "Olena Kovalenko",
        "position": "Sales Representative",
        "role": role,
        "salary": 30_000,
        "currency": "UAH",
    }

    employee = employee_from_payload(payload)

    assert type(employee) is expected_type
    assert employee.salary == Money(30_000)