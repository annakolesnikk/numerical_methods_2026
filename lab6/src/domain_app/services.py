from collections.abc import Sequence

from domain_app.models import (
    Department,
    Employee,
    PayrollRecord,
)
from domain_app.protocols import (
    Notifier,
    PayrollProvider,
    ReportFormatter,
)
from domain_app.repositories import (
    InMemoryRepository,
)
from domain_app.value_objects import (
    Money,
)


class TextReportFormatter(
    ReportFormatter
):

    def format(
        self,
        records: Sequence[PayrollRecord],
        total: Money,
    ) -> str:

        lines = [
            str(record)
            for record in records
        ]

        lines.append(
            f"Total payroll: {total}"
        )

        return "\n".join(lines)


class CsvReportFormatter(
    ReportFormatter
):

    def format(
        self,
        records: Sequence[PayrollRecord],
        total: Money,
    ) -> str:

        lines = ["period,employee,amount"]

        lines.extend(
            f"{record.period},"
            f"{record.employee.name},"
            f"{record.amount.amount:.2f}"
            for record in records
        )

        lines.append(
            f"total,,{total.amount:.2f}"
        )

        return "\n".join(lines)


class ConsoleNotifier:

    def send(
        self,
        recipient: str,
        message: str,
    ) -> None:

        print(
            f"Notification to "
            f"{recipient}:\n"
            f"{message}"
        )


class EmployeeService:

    def __init__(
        self,
        repository: InMemoryRepository[
            Employee
        ],
    ) -> None:

        self._employees = repository

    def add_employee(
        self,
        employee: Employee,
        department: Department | None = None,
    ) -> None:

        if self._employees.get(
            employee.id
        ) is not None:
            raise ValueError(
                "Employee already exists"
            )

        self._employees.add(
            employee
        )

        if department is not None:
            department.add(
                employee
            )

    def assign_department(
        self,
        employee_id: int,
        department: Department,
    ) -> None:

        employee = self._employees.get(
            employee_id
        )

        if employee is None:
            raise ValueError(
                "Employee not found"
            )

        department.add(
            employee
        )

    def find_by_department(
        self,
        department_name: str,
    ) -> list[Employee]:

        return [
            employee
            for employee in self._employees.all()
            if employee.department_name is not None
            and employee.department_name.lower()
            == department_name.lower()
        ]


class PayrollService:

    def __init__(
        self,
        repository: InMemoryRepository[
            Employee
        ],
        notifier: Notifier,
        formatter: ReportFormatter,
    ) -> None:

        self._employees = repository
        self._notifier = notifier
        self._formatter = formatter

    def average_salary(
        self,
    ) -> Money:

        employees = self._employees.all()

        if not employees:
            return Money(0)

        total = sum(
            employee.salary.amount
            for employee in employees
        )

        return Money(
            total / len(employees)
        )

    def highest_paid(
        self,
    ) -> Employee | None:

        employees = self._employees.all()

        if not employees:
            return None

        return max(
            employees,
            key=lambda employee: employee.salary.amount,
        )

    def build_payroll(
        self,
        period: str,
    ) -> list[PayrollRecord]:

        return [
            PayrollRecord(
                id=index,
                employee=employee,
                period=period,
                amount=employee.monthly_pay(),
            )
            for index, employee in enumerate(
                self._employees.all(),
                start=1,
            )
        ]

    def total_payroll(
        self,
        records: Sequence[PayrollRecord],
    ) -> Money:

        total = Money(0)

        for record in records:
            total = total + record.amount

        return total

    def send_report(
        self,
        period: str,
        recipient: str,
    ) -> Money:

        records = self.build_payroll(
            period
        )

        total = self.total_payroll(
            records
        )

        report = self._formatter.format(
            records,
            total,
        )

        self._notifier.send(
            recipient,
            report,
        )

        return total



class AsyncPayrollService:

    def __init__(
        self,
        repository: InMemoryRepository[
            Employee
        ],
        provider: PayrollProvider,
        formatter: ReportFormatter,
        notifier: Notifier,
    ) -> None:

        self._employees = repository
        self._provider = provider
        self._formatter = formatter
        self._notifier = notifier

    async def build_payroll(
        self,
        period: str,
    ) -> list[PayrollRecord]:

        records = []

        for index, employee in enumerate(
            self._employees.all(),
            start=1,
        ):
            amount = await self._provider.fetch_monthly_pay(
                employee.id,
                period,
            )

            records.append(
                PayrollRecord(
                    id=index,
                    employee=employee,
                    period=period,
                    amount=amount,
                )
            )

        return records

    async def send_report(
        self,
        period: str,
        recipient: str,
    ) -> Money:

        records = await self.build_payroll(
            period
        )

        total = Money(0)

        for record in records:
            total = total + record.amount

        report = self._formatter.format(
            records,
            total,
        )

        self._notifier.send(
            recipient,
            report,
        )

        return total    