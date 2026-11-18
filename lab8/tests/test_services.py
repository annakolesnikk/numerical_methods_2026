import pytest

from employee_manager.models import Employee
from employee_manager.repositories import EmployeeRepository
from employee_manager.services import DepartmentPayroll, EmployeeService, transfer_employees


def test_salary_aggregates(session, staff, departments) -> None:
    service = EmployeeService(session)

    assert service.average_salary() == pytest.approx(49_250)
    assert service.average_salary(departments["IT"].id) == pytest.approx(58_500)
    assert service.total_payroll() == pytest.approx(197_000)
    best = service.highest_paid()
    assert best is not None and best.name == "Oleh Ivanenko"


def test_aggregates_on_empty_database(session) -> None:
    service = EmployeeService(session)

    assert service.average_salary() == 0.0
    assert service.total_payroll() == 0.0
    assert service.highest_paid() is None


def test_payroll_by_department(session, staff) -> None:
    report = EmployeeService(session).payroll_by_department()

    assert report == [
        DepartmentPayroll("Finance", 1, 38_000, 38_000),
        DepartmentPayroll("IT", 2, 117_000, 58_500),
        DepartmentPayroll("Sales", 1, 42_000, 42_000),
    ]


def test_transfer_employees(session, staff, departments) -> None:
    transfer_employees(session, [staff[1].id, staff[3].id], departments["Sales"].id)

    names = [employee.name for employee in EmployeeRepository(session).find_by_department("Sales")]
    assert names == ["Andrii Shevchenko", "Anna Kolesnik", "Oleh Ivanenko"]


def test_transfer_rollback(session, staff, departments) -> None:
    with pytest.raises(ValueError, match="999 not found"):
        transfer_employees(session, [staff[1].id, 999], departments["Sales"].id)

    session.expire_all()
    employee = session.get(Employee, staff[1].id)
    assert employee is not None
    assert employee.department_id == departments["IT"].id


def test_transfer_to_missing_department(session, staff, departments) -> None:
    with pytest.raises(ValueError, match="Department not found"):
        transfer_employees(session, [staff[0].id], 999)

    session.expire_all()
    assert session.get(Employee, staff[0].id).department_id == departments["Sales"].id