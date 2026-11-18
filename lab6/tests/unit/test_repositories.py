from domain_app.models import Employee
from domain_app.repositories import InMemoryRepository


def test_remove_existing_employee(repository: InMemoryRepository[Employee]) -> None:
    assert repository.remove(1) is True
    assert repository.get(1) is None
    assert len(repository.all()) == 2


def test_remove_missing_employee_returns_false(
    repository: InMemoryRepository[Employee],
) -> None:
    assert repository.remove(999) is False
    assert len(repository.all()) == 3