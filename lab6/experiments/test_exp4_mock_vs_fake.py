from unittest.mock import Mock

from domain_app.models import Employee
from domain_app.repositories import InMemoryRepository
from domain_app.services import EmployeeService
from domain_app.value_objects import Money


class FakeRepository:
    def __init__(self) -> None:
        self.items: dict[int, Employee] = {}

    def add(self, item: Employee) -> None:
        self.items[item.id] = item

    def get(self, item_id: int) -> Employee | None:
        return self.items.get(item_id)

    def all(self) -> list[Employee]:
        return list(self.items.values())


def make_employee() -> Employee:
    return Employee(id=1, name="Anna Kolesnik", position="Manager", _salary=Money(42_000))


def test_add_employee_with_mock() -> None:
    repository = Mock(spec=InMemoryRepository)
    repository.get.return_value = None
    employee = make_employee()

    EmployeeService(repository).add_employee(employee)

    repository.add.assert_called_once_with(employee)


def test_add_employee_with_fake() -> None:
    repository = FakeRepository()
    employee = make_employee()

    EmployeeService(repository).add_employee(employee)  # type: ignore[arg-type]

    assert repository.get(1) is employee
    assert repository.all() == [employee]