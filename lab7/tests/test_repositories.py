from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from employee_manager.models import Employee
from employee_manager.repositories import DepartmentRepository, EmployeeRepository


# ---------- Employee CRUD ----------

def test_add_employee(session, departments) -> None:
    repository = EmployeeRepository(session)

    saved = repository.add(
        Employee(
            name="Anna Kolesnik",
            position="Sales Manager",
            salary=42_000,
            department_id=departments["Sales"].id,
            hire_date=date(2024, 3, 1),
        )
    )

    assert saved.id is not None
    assert saved.name == "Anna Kolesnik"
    assert saved.hire_date == date(2024, 3, 1)


def test_get_employee(session, staff) -> None:
    repository = EmployeeRepository(session)

    loaded = repository.get_by_id(staff[1].id)

    assert loaded is not None
    assert loaded.name == "Oleh Ivanenko"
    assert loaded.department.name == "IT"
    assert len(repository.get_all()) == 4


def test_update_position_and_salary(session, staff) -> None:
    repository = EmployeeRepository(session)

    repository.update_position(staff[1].id, "Team Lead")
    updated = repository.update_salary(staff[1].id, 70_000)

    assert updated is not None
    assert updated.position == "Team Lead"
    assert updated.salary == 70_000


def test_update_missing_employee_returns_none(session) -> None:
    repository = EmployeeRepository(session)

    assert repository.update_salary(999, 1_000) is None
    assert repository.update_position(999, "Nobody") is None


def test_delete_employee(session, staff) -> None:
    repository = EmployeeRepository(session)

    assert repository.delete(staff[0].id) is True
    assert repository.get_by_id(staff[0].id) is None
    assert repository.delete(staff[0].id) is False


def test_find_by_department(session, staff) -> None:
    repository = EmployeeRepository(session)

    found = repository.find_by_department("IT")

    assert [employee.name for employee in found] == ["Andrii Shevchenko", "Oleh Ivanenko"]
    assert repository.find_by_department("Legal") == []


# ---------- Department CRUD ----------

def test_department_crud(session) -> None:
    repository = DepartmentRepository(session)

    created = repository.add("HR")
    assert repository.get_by_name("HR") is created

    renamed = repository.rename(created.id, "People")
    assert renamed is not None and renamed.name == "People"
    assert [department.name for department in repository.get_all()] == ["People"]

    assert repository.delete(created.id) is True
    assert repository.get_by_id(created.id) is None
    assert repository.rename(created.id, "X") is None
    assert repository.delete(created.id) is False


def test_delete_department_cascades_to_employees(session, departments, staff) -> None:
    DepartmentRepository(session).delete(departments["IT"].id)

    assert EmployeeRepository(session).find_by_department("IT") == []
    assert len(EmployeeRepository(session).get_all()) == 2


# ---------- Constraints ----------

def test_unique_department_name(session, departments) -> None:
    repository = DepartmentRepository(session)

    with pytest.raises(IntegrityError):
        repository.add("Sales")

    assert len(repository.get_all()) == 3


def test_negative_salary_violates_check_constraint(session, departments) -> None:
    repository = EmployeeRepository(session)

    with pytest.raises(IntegrityError):
        repository.add(
            Employee(
                name="Bad Salary",
                position="Tester",
                salary=-1,
                department_id=departments["IT"].id,
            )
        )

    assert repository.get_all() == []


def test_foreign_key_is_enforced(session) -> None:
    repository = EmployeeRepository(session)

    with pytest.raises(IntegrityError):
        repository.add(
            Employee(name="No Department", position="Tester", salary=1_000, department_id=999)
        )