from collections.abc import AsyncIterator, Iterator

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from employee_manager.api import app
from employee_manager.database import enable_sqlite_foreign_keys
from employee_manager.dependencies import get_http_client, get_session
from employee_manager.models import Base, Department, Employee
from employee_manager.repositories import DepartmentRepository, EmployeeRepository


# ---------- Lab 7: repository fixtures ----------

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


# ---------- Lab 8: API fixtures ----------

@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(engine, "connect", enable_sqlite_foreign_keys)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_session() -> Iterator[Session]:
        with TestSession() as session:
            yield session

    async def override_get_http_client() -> AsyncIterator[httpx.AsyncClient]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http:
            yield http

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_http_client] = override_get_http_client

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def api_data(client: TestClient) -> dict[str, int]:
    ids = {}
    for name in ("Sales", "IT"):
        ids[name] = client.post("/departments", json={"name": name}).json()["id"]
    for name, position, department, salary in [
        ("Anna Kolesnik", "Sales Manager", "Sales", 42_000),
        ("Oleh Ivanenko", "Backend Developer", "IT", 65_000),
        ("Andrii Shevchenko", "Frontend Developer", "IT", 52_000),
    ]:
        client.post(
            "/employees",
            json={
                "name": name,
                "position": position,
                "salary": salary,
                "department_id": ids[department],
            },
        )
    return ids