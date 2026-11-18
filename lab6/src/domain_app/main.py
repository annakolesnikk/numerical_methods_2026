from domain_app.dto import (
    EmployeePayload,
    employee_from_payload,
)
from domain_app.models import (
    Department,
    Developer,
    Employee,
    Manager,
)
from domain_app.repositories import (
    InMemoryRepository,
)
from domain_app.services import (
    ConsoleNotifier,
    CsvReportFormatter,
    EmployeeService,
    PayrollService,
    TextReportFormatter,
)
from domain_app.value_objects import (
    Money,
)


def main() -> None:

    sales = Department(
        id=1,
        name="Sales",
    )

    it = Department(
        id=2,
        name="IT",
    )

    finance = Department(
        id=3,
        name="Finance",
    )

    repository = (
        InMemoryRepository[
            Employee
        ]()
    )

    employee_service = EmployeeService(
        repository,
    )

    employee_service.add_employee(
        Manager(
            id=1,
            name="Anna Kolesnik",
            position="Sales Manager",
            _salary=Money(42_000),
            bonus=Money(8_000),
        ),
        sales,
    )

    employee_service.add_employee(
        Developer(
            id=2,
            name="Oleh Ivanenko",
            position="Backend Developer",
            _salary=Money(65_000),
            level="Senior",
        ),
        it,
    )

    employee_service.add_employee(
        Employee(
            id=3,
            name="Iryna Petrenko",
            position="Accountant",
            _salary=Money(38_000),
        ),
        finance,
    )

    employee_service.add_employee(
        Developer(
            id=4,
            name="Andrii Shevchenko",
            position="Frontend Developer",
            _salary=Money(52_000),
            level="Middle",
        ),
    )

    employee_service.assign_department(
        4,
        it,
    )

    payload: EmployeePayload = {
        "id": 5,
        "name": "Olena Kovalenko",
        "position": "Sales Representative",
        "role": "employee",
        "salary": 30_000,
        "currency": "UAH",
    }

    employee_service.add_employee(
        employee_from_payload(payload),
        sales,
    )

    print("All employees:")

    for employee in repository.all():
        print(
            f"{employee.id}. {employee} | "
            f"salary: {employee.salary} | "
            f"monthly pay: {employee.monthly_pay()}"
        )

    print(
        "\nDepartment IT:",
        len(it),
        "employees",
    )

    for employee in it:
        print("-", employee.name)

    print(
        "Employee 2 in IT:",
        2 in it,
    )
    print(
        "Employee 3 in IT:",
        3 in it,
    )
    print(
        "IT total salary:",
        it.total_salary,
    )

    print("\nSearch by department Sales:")

    for employee in employee_service.find_by_department(
        "sales"
    ):
        print("-", employee.name)

    payroll_service = PayrollService(
        repository=repository,
        notifier=ConsoleNotifier(),
        formatter=TextReportFormatter(),
    )

    print(
        "\nAverage salary:",
        payroll_service.average_salary(),
    )

    best = payroll_service.highest_paid()

    if best is not None:
        print(
            "Highest salary:",
            best.name,
            best.salary,
        )

    print()

    total = payroll_service.send_report(
        period="2026-11",
        recipient="hr@example.com",
    )

    print(
        "\nTotal payroll fund:",
        total,
    )

    csv_service = PayrollService(
        repository=repository,
        notifier=ConsoleNotifier(),
        formatter=CsvReportFormatter(),
    )

    print()

    csv_service.send_report(
        period="2026-11",
        recipient="accounting@example.com",
    )

    try:
        Money(-100)
    except ValueError as error:
        print(
            "\nValidation error:",
            error,
        )


if __name__ == "__main__":
    main()


