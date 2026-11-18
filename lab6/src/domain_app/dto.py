from typing import (
    NotRequired,
    TypedDict,
)

from domain_app.models import (
    Developer,
    Employee,
    Manager,
)
from domain_app.value_objects import (
    Money,
)


class EmployeePayload(
    TypedDict
):
    id: int
    name: str
    position: str
    role: str
    salary: float
    currency: str
    bonus: NotRequired[float]
    level: NotRequired[str]


def employee_from_payload(
    data: EmployeePayload,
) -> Employee:

    salary = Money(
        amount=data["salary"],
        currency=data["currency"],
    )

    if data["role"] == "manager":
        return Manager(
            id=data["id"],
            name=data["name"],
            position=data["position"],
            _salary=salary,
            bonus=Money(
                data.get("bonus", 0.0),
                data["currency"],
            ),
        )

    if data["role"] == "developer":
        return Developer(
            id=data["id"],
            name=data["name"],
            position=data["position"],
            _salary=salary,
            level=data.get("level", "Junior"),
        )

    return Employee(
        id=data["id"],
        name=data["name"],
        position=data["position"],
        _salary=salary,
    )