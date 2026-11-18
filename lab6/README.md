# Employee Testing

Laboratory work No. 6 for the course "Professional Python".

## Description

Automated test suite (variant 6, employee management system) for the code
of laboratory works No. 4 (`domain_app`) and No. 5 (`reliable_importer`):
unit and integration tests, fixtures, parametrization, tmp_path,
monkeypatch, Mock, AsyncMock, statement and branch coverage.

## Installation

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Run tests

```
pytest -v --cov=domain_app --cov=reliable_importer --cov-branch --cov-report=term-missing --cov-report=html
```

Only unit tests: `pytest -m "not integration"`
Only integration tests: `pytest -m integration`

## Author

Student: Anna Kolesnik
Group: FEP-33