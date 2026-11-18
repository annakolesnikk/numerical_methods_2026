from unittest.mock import AsyncMock, Mock

import pytest

from domain_app.models import Department, Developer, Employee, Manager
from domain_app.protocols import Notifier
from domain_app.repositories import InMemoryRepository
from domain_app.services import (
    AsyncPayrollService,
    CsvReportFormatter,
    EmployeeService,
    PayrollService,
)
from domain_app.value_objects import Money

pytestmark = pytest.mark.integration


def test_employee_to_payroll_to_csv_report(manager: Manager, developer: Developer) -> None:
    repository = InMemoryRepository[Employee]()
    employees = EmployeeService(repository)
    sales = Department(id=1, name="Sales")
    it = Department(id=2, name="IT")
    employees.add_employee(manager, sales)
    employees.add_employee(developer, it)
    notifier = Mock(spec=Notifier)
    payroll = PayrollService(repository, notifier, CsvReportFormatter())

    total = payroll.send_report("2026-11", "accounting@example.com")

    recipient, report = notifier.send.call_args.args
    assert recipient == "accounting@example.com"
    assert report.splitlines() == [
        "period,employee,amount",
        "2026-11,Anna Kolesnik,50000.00",
        "2026-11,Oleh Ivanenko,65000.00",
        "total,,115000.00",
    ]
    assert total == Money(115_000)
    assert sales.total_salary == Money(42_000)


@pytest.mark.asyncio
async def test_async_provider_to_report(repository: InMemoryRepository[Employee]) -> None:
    amounts = {1: Money(50_000), 2: Money(65_000), 3: Money(38_000)}
    provider = AsyncMock()
    provider.fetch_monthly_pay.side_effect = lambda employee_id, period: amounts[employee_id]
    notifier = Mock(spec=Notifier)
    service = AsyncPayrollService(repository, provider, CsvReportFormatter(), notifier)

    total = await service.send_report("2026-11", "hr@example.com")

    assert total.amount == pytest.approx(153_000)
    report = notifier.send.call_args.args[1]
    assert "2026-11,Iryna Petrenko,38000.00" in report
    assert report.endswith("total,,153000.00")