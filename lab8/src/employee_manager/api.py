import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from employee_manager.database import engine
from employee_manager.dependencies import get_http_client, get_session
from employee_manager.external_api import fetch_departments_statistics
from employee_manager.models import Base, Department, Employee
from employee_manager.repositories import DepartmentRepository, EmployeeRepository
from employee_manager.schemas import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentStatisticsResponse,
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    SalaryStatisticsResponse,
)
from employee_manager.services import EmployeeService, transfer_employees


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Employee Manager API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Database constraint violated"},
    )


def get_department_or_404(session: Session, department_id: int) -> Department:
    department = DepartmentRepository(session).get_by_id(department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return department


def get_employee_or_404(session: Session, employee_id: int) -> Employee:
    employee = EmployeeRepository(session).get_by_id(employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Employee Manager API", "docs": "/docs"}


# ---------- departments ----------

@app.get("/departments", response_model=list[DepartmentResponse])
async def get_departments(session: Session = Depends(get_session)) -> list[Department]:
    return DepartmentRepository(session).get_all()


@app.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_department(
    data: DepartmentCreate,
    session: Session = Depends(get_session),
) -> Department:
    return DepartmentRepository(session).add(data.name)


@app.get("/departments/{department_id}/employees", response_model=list[EmployeeResponse])
async def get_department_employees(
    department_id: int,
    session: Session = Depends(get_session),
) -> list[Employee]:
    get_department_or_404(session, department_id)
    return EmployeeRepository(session).search(department_id=department_id)


@app.get(
    "/departments/{department_id}/statistics",
    response_model=DepartmentStatisticsResponse,
)
async def get_department_statistics(
    department_id: int,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    department = get_department_or_404(session, department_id)
    statistics = EmployeeService(session).salary_statistics(department_id)
    return {
        "department_id": department.id,
        "department": department.name,
        **statistics.__dict__,
    }


@app.post(
    "/departments/statistics/batch",
    response_model=list[DepartmentStatisticsResponse],
)
async def get_departments_statistics_batch(
    department_ids: list[int],
    client: httpx.AsyncClient = Depends(get_http_client),
) -> list[dict[str, Any]]:
    try:
        return await asyncio.wait_for(
            fetch_departments_statistics(client, department_ids),
            timeout=10.0,
        )
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Batch operation timed out",
        )
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=error.response.status_code,
            detail=error.response.json().get("detail", "Upstream error"),
        )


# ---------- employees ----------

@app.get("/employees", response_model=list[EmployeeResponse])
async def get_employees(
    department_id: int | None = Query(default=None, gt=0),
    min_salary: float | None = Query(default=None, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[Employee]:
    return EmployeeRepository(session).search(department_id, min_salary, limit, offset)


@app.get("/employees/statistics", response_model=SalaryStatisticsResponse)
async def get_employees_statistics(session: Session = Depends(get_session)) -> Any:
    return EmployeeService(session).salary_statistics()


@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    session: Session = Depends(get_session),
) -> Employee:
    return get_employee_or_404(session, employee_id)


@app.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(
    data: EmployeeCreate,
    session: Session = Depends(get_session),
) -> Employee:
    get_department_or_404(session, data.department_id)
    return EmployeeRepository(session).add(Employee(**data.model_dump()))


@app.patch("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    session: Session = Depends(get_session),
) -> Employee:
    repository = EmployeeRepository(session)
    employee = get_employee_or_404(session, employee_id)

    if data.department_id is not None:
        get_department_or_404(session, data.department_id)
        transfer_employees(session, [employee_id], data.department_id)
    if data.position is not None:
        repository.update_position(employee_id, data.position)
    if data.salary is not None:
        repository.update_salary(employee_id, data.salary)

    session.refresh(employee)
    return employee


@app.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    session: Session = Depends(get_session),
) -> None:
    get_employee_or_404(session, employee_id)
    EmployeeRepository(session).delete(employee_id)