import logging
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from domain_app.models import Department, Developer, Employee, Manager
from domain_app.repositories import InMemoryRepository
from domain_app.value_objects import Money

CSV_HEADER = "employee_id,name,position,department,salary\n"


@pytest.fixture
def manager() -> Manager:
    return Manager(
        id=1,
        name="Anna Kolesnik",
        position="Sales Manager",
        _salary=Money(42_000),
        bonus=Money(8_000),
    )


@pytest.fixture
def developer() -> Developer:
    return Developer(
        id=2,
        name="Oleh Ivanenko",
        position="Backend Developer",
        _salary=Money(65_000),
        level="Senior",
    )


@pytest.fixture
def accountant() -> Employee:
    return Employee(
        id=3,
        name="Iryna Petrenko",
        position="Accountant",
        _salary=Money(38_000),
    )


@pytest.fixture
def repository(
    manager: Manager,
    developer: Developer,
    accountant: Employee,
) -> InMemoryRepository[Employee]:
    repository = InMemoryRepository[Employee]()
    for employee in (manager, developer, accountant):
        repository.add(employee)
    return repository


@pytest.fixture
def it_department() -> Department:
    return Department(id=2, name="IT")


@pytest.fixture
def employee_factory() -> Callable[..., Employee]:
    def create_employee(
        *,
        employee_id: int = 100,
        name: str = "Test Employee",
        salary: float = 30_000,
    ) -> Employee:
        return Employee(
            id=employee_id,
            name=name,
            position="Tester",
            _salary=Money(salary),
        )

    return create_employee


@pytest.fixture
def csv_factory(tmp_path: Path) -> Callable[[str], Path]:
    def write_csv(rows: str) -> Path:
        path = tmp_path / "employees.csv"
        path.write_text(CSV_HEADER + rows, encoding="utf-8")
        return path

    return write_csv


@pytest.fixture
def config_factory(tmp_path: Path) -> Callable[..., Path]:
    def write_config(
        *,
        input_path: Path,
        minimum_salary: object = 30000,
        skip_invalid: bool = True,
        departments: str = "[Sales, IT, Finance, HR]",
    ) -> Path:
        path = tmp_path / "config.yaml"
        path.write_text(
            f"input:\n  path: {input_path}\n"
            f"output:\n  path: {tmp_path / 'output' / 'employees.json'}\n"
            f"processing:\n  minimum_salary: {minimum_salary}\n"
            f"  skip_invalid: {str(skip_invalid).lower()}\n"
            f"  allowed_departments: {departments}\n"
            f"logging:\n  level: INFO\n  path: {tmp_path / 'logs' / 'application.log'}\n",
            encoding="utf-8",
        )
        return path

    return write_config


@pytest.fixture(autouse=True)
def close_log_handlers() -> Iterator[None]:
    yield
    root = logging.getLogger()
    for handler in list(root.handlers):
        handler.close()
        root.removeHandler(handler)