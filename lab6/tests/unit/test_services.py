from unittest.mock import Mock, create_autospec

import pytest

from domain_app.models import Department, Employee, PayrollRecord
from domain_app.protocols import Notifier, ReportFormatter
from domain_app.repositories import InMemoryRepository
from domain_app.services import (
    CsvReportFormatter,
    EmployeeService,
    PayrollService,
    TextReportFormatter,
)
from domain_app.value_objects import Money


# ---------- EmployeeService with Mock repository ----------

def test_add_employee_saves_to_repository(accountant: Employee) -> None:
    repository = Mock(spec=InMemoryRepository)
    repository.get.return_value = None
    service = EmployeeService(repository)

    service.add_employee(accountant)

    repository.get.assert_called_once_with(3)
    repository.add.assert_called_once_with(accountant)


def test_add_existing_employee_raises_and_does_not_save(accountant: Employee) -> None:
    repository = Mock(spec=InMemoryRepository)
    repository.get.return_value = accountant
    service = EmployeeService(repository)

    with pytest.raises(ValueError, match="already exists"):
        service.add_employee(accountant)

    repository.add.assert_not_called()


def test_add_employee_with_department(
    repository: InMemoryRepository[Employee],
    employee_factory,
    it_department: Department,
) -> None:
    service = EmployeeService(repository)
    employee = employee_factory(employee_id=50)

    service.add_employee(employee, it_department)

    assert repository.get(50) is employee
    assert employee.department_name == "IT"


def test_assign_department_to_missing_employee_raises(
    repository: InMemoryRepository[Employee],
    it_department: Department,
) -> None:
    service = EmployeeService(repository)

    with pytest.raises(ValueError, match="not found"):
        service.assign_department(999, it_department)

    assert len(it_department) == 0


def test_find_by_department_is_case_insensitive(
    repository: InMemoryRepository[Employee],
    developer,
    it_department: Department,
) -> None:
    service = EmployeeService(repository)
    service.assign_department(developer.id, it_department)

    assert service.find_by_department("it") == [developer]
    assert service.find_by_department("Finance") == []


# ---------- PayrollService ----------

@pytest.fixture
def payroll_service(repository: InMemoryRepository[Employee]) -> PayrollService:
    return PayrollService(
        repository=repository,
        notifier=Mock(spec=Notifier),
        formatter=TextReportFormatter(),
    )


def test_average_salary(payroll_service: PayrollService) -> None:
    # (42000 + 65000 + 38000) / 3 = 48333.333...
    assert payroll_service.average_salary().amount == pytest.approx(48_333.333, rel=1e-6)


def test_highest_paid_employee(payroll_service: PayrollService, developer) -> None:
    assert payroll_service.highest_paid() is developer


def test_empty_repository_statistics() -> None:
    service = PayrollService(
        repository=InMemoryRepository[Employee](),
        notifier=Mock(spec=Notifier),
        formatter=TextReportFormatter(),
    )

    assert service.average_salary() == Money(0)
    assert service.highest_paid() is None
    assert service.build_payroll("2026-11") == []


def test_total_payroll_includes_manager_bonus(payroll_service: PayrollService) -> None:
    records = payroll_service.build_payroll("2026-11")

    total = payroll_service.total_payroll(records)

    # 42000 + 8000 bonus + 65000 + 38000
    assert total.amount == pytest.approx(153_000)
    assert [record.id for record in records] == [1, 2, 3]


def test_send_report_formats_and_notifies(
    repository: InMemoryRepository[Employee],
) -> None:
    formatter = create_autospec(ReportFormatter, instance=True)
    formatter.format.return_value = "REPORT"
    notifier = Mock(spec=Notifier)
    service = PayrollService(repository, notifier, formatter)

    total = service.send_report("2026-11", "hr@example.com")

    assert total.amount == pytest.approx(153_000)
    formatter.format.assert_called_once()
    notifier.send.assert_called_once_with("hr@example.com", "REPORT")


def test_send_report_propagates_notifier_failure(
    repository: InMemoryRepository[Employee],
) -> None:
    notifier = Mock(spec=Notifier)
    notifier.send.side_effect = ConnectionError("SMTP unavailable")
    service = PayrollService(repository, notifier, TextReportFormatter())

    with pytest.raises(ConnectionError, match="SMTP unavailable"):
        service.send_report("2026-11", "hr@example.com")

    notifier.send.assert_called_once()


# ---------- Report formatters ----------

def test_text_report_formatter(accountant: Employee) -> None:
    records = [PayrollRecord(1, accountant, "2026-11", Money(38_000))]

    report = TextReportFormatter().format(records, Money(38_000))

    assert report == (
        "2026-11 Iryna Petrenko: 38000.00 UAH\n"
        "Total payroll: 38000.00 UAH"
    )


def test_csv_report_formatter(accountant: Employee) -> None:
    records = [PayrollRecord(1, accountant, "2026-11", Money(38_000))]

    report = CsvReportFormatter().format(records, Money(38_000))

    assert report.splitlines() == [
        "period,employee,amount",
        "2026-11,Iryna Petrenko,38000.00",
        "total,,38000.00",
    ]


def test_console_notifier_prints_message(capsys: pytest.CaptureFixture[str]) -> None:
    from domain_app.services import ConsoleNotifier

    ConsoleNotifier().send("hr@example.com", "Payroll is ready")

    assert capsys.readouterr().out == "Notification to hr@example.com:\nPayroll is ready\n"    