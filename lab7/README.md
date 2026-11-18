# Employee Manager

Laboratory work No. 7 for the course "Professional Python".

## Description

Employee management application (variant 6) with a persistence layer:
SQLite, SQLAlchemy ORM, Repository Pattern, CRUD, transactions with
commit/rollback, DB-API parameterized query, Alembic migrations and
integration tests.

## Installation

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
```

## Database

```
alembic upgrade head
```

## Run

```
python -m employee_manager.main
```

## Tests

```
pytest -v
```

## Author

Student: Anna Kolesnik
Group: FEP-33