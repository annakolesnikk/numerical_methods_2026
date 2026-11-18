import httpx
import pytest

from employee_manager.api import app


def test_root(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


# ---------- POST ----------

def test_create_department(client) -> None:
    response = client.post("/departments", json={"name": "HR"})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "HR"}


def test_duplicate_department_returns_409(client, api_data) -> None:
    response = client.post("/departments", json={"name": "Sales"})

    assert response.status_code == 409


def test_create_employee(client, api_data) -> None:
    response = client.post(
        "/employees",
        json={
            "name": "Iryna Petrenko",
            "position": "Accountant",
            "salary": 38_000,
            "department_id": api_data["Sales"],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 4
    assert data["name"] == "Iryna Petrenko"
    assert data["salary"] == 38_000


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "A", "position": "Tester", "salary": 1000, "department_id": 1},
        {"name": "Anna Kolesnik", "position": "Tester", "salary": -1, "department_id": 1},
        {"name": "Anna Kolesnik", "position": "Tester", "salary": 1000, "department_id": 0},
        {"name": "Anna Kolesnik", "position": "Tester"},
    ],
    ids=["short-name", "negative-salary", "zero-department", "missing-fields"],
)
def test_create_employee_validation(client, payload) -> None:
    response = client.post("/employees", json=payload)

    assert response.status_code == 422


def test_create_employee_unknown_department(client) -> None:
    response = client.post(
        "/employees",
        json={"name": "Anna Kolesnik", "position": "Tester", "salary": 1000, "department_id": 99},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Department not found"


# ---------- GET ----------

def test_get_employees(client, api_data) -> None:
    response = client.get("/employees")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == [
        "Anna Kolesnik",
        "Oleh Ivanenko",
        "Andrii Shevchenko",
    ]


def test_get_employees_with_query_parameters(client, api_data) -> None:
    response = client.get(
        "/employees",
        params={"department_id": api_data["IT"], "min_salary": 60_000},
    )

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Oleh Ivanenko"]


def test_get_employees_pagination(client, api_data) -> None:
    response = client.get("/employees", params={"limit": 1, "offset": 1})

    assert [item["id"] for item in response.json()] == [2]


def test_get_employee(client, api_data) -> None:
    response = client.get("/employees/2")

    assert response.status_code == 200
    assert response.json()["position"] == "Backend Developer"


def test_get_missing_employee_returns_404(client) -> None:
    response = client.get("/employees/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


# ---------- PATCH ----------

def test_update_position_and_salary(client, api_data) -> None:
    response = client.patch("/employees/2", json={"position": "Team Lead", "salary": 70_000})

    assert response.status_code == 200
    assert response.json()["position"] == "Team Lead"
    assert response.json()["salary"] == 70_000


def test_transfer_employee(client, api_data) -> None:
    response = client.patch("/employees/3", json={"department_id": api_data["Sales"]})

    assert response.status_code == 200
    assert response.json()["department_id"] == api_data["Sales"]


def test_update_validation_and_missing(client, api_data) -> None:
    assert client.patch("/employees/1", json={"salary": -5}).status_code == 422
    assert client.patch("/employees/999", json={"salary": 5}).status_code == 404
    assert client.patch("/employees/1", json={"department_id": 99}).status_code == 404


# ---------- DELETE ----------

def test_delete_employee(client, api_data) -> None:
    response = client.delete("/employees/1")

    assert response.status_code == 204
    assert client.get("/employees/1").status_code == 404
    assert client.delete("/employees/1").status_code == 404


# ---------- departments / statistics ----------

def test_department_employees(client, api_data) -> None:
    response = client.get(f"/departments/{api_data['IT']}/employees")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert client.get("/departments/99/employees").status_code == 404


def test_department_statistics(client, api_data) -> None:
    response = client.get(f"/departments/{api_data['IT']}/statistics")

    assert response.status_code == 200
    assert response.json() == {
        "department_id": api_data["IT"],
        "department": "IT",
        "employees_count": 2,
        "average_salary": 58_500,
        "max_salary": 65_000,
        "total_payroll": 117_000,
    }


def test_employees_statistics(client, api_data) -> None:
    response = client.get("/employees/statistics")

    assert response.json() == {
        "employees_count": 3,
        "average_salary": pytest.approx(53_000),
        "max_salary": 65_000,
        "total_payroll": 159_000,
    }


def test_batch_statistics(client, api_data) -> None:
    response = client.post("/departments/statistics/batch", json=[api_data["Sales"], api_data["IT"]])

    assert response.status_code == 200
    assert [item["total_payroll"] for item in response.json()] == [42_000, 117_000]


def test_batch_statistics_missing_department(client, api_data) -> None:
    response = client.post("/departments/statistics/batch", json=[api_data["IT"], 99])

    assert response.status_code == 404


# ---------- async API test via HTTPX ----------

@pytest.mark.asyncio
async def test_async_api_root() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200