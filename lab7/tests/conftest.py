from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from employee_manager.database import enable_sqlite_foreign_keys
from employee_manager.models import Base, Department, Employee
from employee_manager.repositories import DepartmentRepository, EmployeeRepository


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")
    event.listen(engine, "connect", enable_sqlite_foreign_keys)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    with TestSession() as session:
        yield session

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def departments(session: Session) -> dict[str, Department]:
    repository = DepartmentRepository(session)
    return {name: repository.add(name) for name in ("Sales", "IT", "Finance")}


@pytest.fixture
def staff(session: Session, departments: dict[str, Department]) -> list[Employee]:
    repository = EmployeeRepository(session)
    data = [
        ("Anna Kolesnik", "Sales Manager", "Sales", 42_000),
        ("Oleh Ivanenko", "Backend Developer", "IT", 65_000),
        ("Iryna Petrenko", "Accountant", "Finance", 38_000),
        ("Andrii Shevchenko", "Frontend Developer", "IT", 52_000),
    ]
    return [
        repository.add(
            Employee(
                name=name,
                position=position,
                salary=salary,
                department_id=departments[department].id,
            )
        )
        for name, position, department, salary in data
    ]