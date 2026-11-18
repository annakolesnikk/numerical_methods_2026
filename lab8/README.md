# Employee Manager

Laboratory work No. 8 for the course "Professional Python".

## Description

REST API for the employee management system (variant 6) built with FastAPI:
Pydantic schemas and validation, CRUD endpoints for employees, department
statistics, persistence layer from laboratory work No. 7 (SQLite,
SQLAlchemy, Repository Pattern), asynchronous statistics loading with
httpx.AsyncClient, asyncio.Task, asyncio.gather, Semaphore, timeout and retry.

## Installation

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
alembic upgrade head
```

## Run API

```
uvicorn employee_manager.api:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

## Async client

```
python -m employee_manager.external_api
```

## Tests

```
pytest -v
```

## Author

Student: Anna Kolesnik
Group: FEP-33