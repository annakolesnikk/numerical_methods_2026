from collections.abc import Iterator
from dataclasses import (
    dataclass,
    field,
)

from domain_app.value_objects import (
    Money,
)


@dataclass
class Employee:
    id: int
    name: str
    position: str
    _salary: Money
    department_name: str | None = None

    @property
    def salary(
        self,
    ) -> Money:
        return self._salary

    def change_salary(
        self,
        new_salary: Money,
    ) -> None:

        if (
            new_salary.currency
            != self._salary.currency
        ):
            raise ValueError(
                "Currency mismatch"
            )

        self._salary = new_salary

    def monthly_pay(
        self,
    ) -> Money:

        return self.salary

    def describe(
        self,
    ) -> str:

        department = (
            self.department_name
            or "no department"
        )

        return (
            f"{self.name} "
            f"({self.position}, "
            f"{department})"
        )

    def __str__(
        self,
    ) -> str:

        return self.describe()


@dataclass
class Manager(Employee):
    bonus: Money = field(
        default_factory=lambda: Money(0)
    )

    def monthly_pay(
        self,
    ) -> Money:

        return (
            super().monthly_pay()
            + self.bonus
        )

    def describe(
        self,
    ) -> str:

        return (
            f"{super().describe()} "
            f"bonus: {self.bonus}"
        )


@dataclass
class Developer(Employee):
    level: str = "Junior"

    def describe(
        self,
    ) -> str:

        return (
            f"{super().describe()} "
            f"level: {self.level}"
        )


@dataclass
class Department:
    id: int
    name: str
    employees: list[
        Employee
    ] = field(
        default_factory=list
    )

    def add(
        self,
        employee: Employee,
    ) -> None:

        if employee.id in self:
            raise ValueError(
                "Employee already "
                "in department"
            )

        if (
            employee.department_name is not None
            and employee.department_name != self.name
        ):
            raise ValueError(
                "Employee already belongs "
                f"to department {employee.department_name}"
            )

        employee.department_name = self.name

        self.employees.append(
            employee
        )

    def __len__(
        self,
    ) -> int:

        return len(
            self.employees
        )

    def __iter__(
        self,
    ) -> Iterator[Employee]:

        return iter(
            self.employees
        )

    def __contains__(
        self,
        employee_id: object,
    ) -> bool:

        return any(
            employee.id
            == employee_id
            for employee in self.employees
        )

    @property
    def total_salary(
        self,
    ) -> Money:

        total = Money(0)

        for employee in self.employees:
            total = total + employee.salary

        return total


@dataclass(
    frozen=True,
)
class PayrollRecord:
    id: int
    employee: Employee
    period: str
    amount: Money

    def __str__(
        self,
    ) -> str:

        return (
            f"{self.period} "
            f"{self.employee.name}: "
            f"{self.amount}"
        )