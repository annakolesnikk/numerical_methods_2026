from unittest.mock import AsyncMock, Mock

import pytest

from domain_app.models import Employee
from domain_app.protocols import Notifier
from domain_app.repositories import InMemoryRepository
from domain_app.services import AsyncPayrollService, TextReportFormatter
from domain_app.value_objects import Money


@pytest.mark.asyncio
async def test_async_payroll_uses_provider_amounts(
    repository: InMemoryRepository[Employee],
) -> None:
    provider = AsyncMock()
    provider.fetch_monthly_pay.return_value = Money(10_000)
    service = AsyncPayrollService(
        repository, provider, TextReportFormatter(), Mock(spec=Notifier)
    )

    records = await service.build_payroll("2026-11")

    assert [record.amount for record in records] == [Money(10_000)] * 3
    assert provider.fetch_monthly_pay.await_count == 3
    provider.fetch_monthly_pay.assert_any_await(2, "2026-11")


@pytest.mark.asyncio
async def test_async_send_report_notifies_with_total(
    accountant: Employee,
) -> None:
    repository = InMemoryRepository[Employee]()
    repository.add(accountant)
    provider = AsyncMock()
    provider.fetch_monthly_pay.return_value = Money(38_000)
    notifier = Mock(spec=Notifier)
    service = AsyncPayrollService(repository, provider, TextReportFormatter(), notifier)

    total = await service.send_report("2026-11", "hr@example.com")

    assert total == Money(38_000)
    provider.fetch_monthly_pay.assert_awaited_once_with(3, "2026-11")
    notifier.send.assert_called_once_with(
        "hr@example.com",
        "2026-11 Iryna Petrenko: 38000.00 UAH\nTotal payroll: 38000.00 UAH",
    )


@pytest.mark.asyncio
async def test_async_provider_failure_does_not_send_report(
    repository: InMemoryRepository[Employee],
) -> None:
    provider = AsyncMock()
    provider.fetch_monthly_pay.side_effect = ConnectionError("Payroll API down")
    notifier = Mock(spec=Notifier)
    service = AsyncPayrollService(repository, provider, TextReportFormatter(), notifier)

    with pytest.raises(ConnectionError, match="Payroll API down"):
        await service.send_report("2026-11", "hr@example.com")

    notifier.send.assert_not_called()