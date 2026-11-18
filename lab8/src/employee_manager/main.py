from employee_manager.database import DATABASE_PATH, SessionLocal, engine
from employee_manager.db_api import find_employees_by_department
from employee_manager.models import Base, Employee
from employee_manager.repositories import DepartmentRepository, EmployeeRepository
from employee_manager.services import EmployeeService, transfer_employees

SEED = [
    ("Anna Kolesnik", "Sales Manager", "Sales", 42_000),
    ("Oleh Ivanenko", "Backend Developer", "IT", 65_000),
    ("Iryna Petrenko", "Accountant", "Finance", 38_000),
    ("Andrii Shevchenko", "Frontend Developer", "IT", 52_000),
    ("Olena Kovalenko", "Sales Representative", "Sales", 30_000),
]


def print_employees(employees: list[Employee]) -> None:
    for item in employees:
        print(
            f"{item.id:3} {item.name:20} {item.position:22} "
            f"{item.department.name:8} {item.salary:10.2f}"
        )


def main() -> None:
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        departments = DepartmentRepository(session)
        employees = EmployeeRepository(session)
        service = EmployeeService(session)

        # Create (only on the first run)
        if not employees.get_all():
            for name, position, department_name, salary in SEED:
                department = departments.get_by_name(department_name)
                if department is None:
                    department = departments.add(department_name)
                employees.add(
                    Employee(
                        name=name,
                        position=position,
                        salary=salary,
                        department_id=department.id,
                    )
                )

        # Read
        print("Employees:")
        print_employees(employees.get_all())

        # Update
        employees.update_position(2, "Team Lead")
        employees.update_salary(2, 70_000)

        sales = departments.get_by_name("Sales")
        assert sales is not None

        # Delete
        temporary = employees.add(
            Employee(name="Temp Worker", position="Intern", salary=0, department_id=sales.id)
        )
        employees.delete(temporary.id)

        # Transaction: transfer + rollback
        transfer_employees(session, [4], sales.id)

        try:
            transfer_employees(session, [3, 999], sales.id)
        except ValueError as error:
            print(f"\nTransfer failed, rollback: {error}")

        print("\nAfter update and transfer:")
        print_employees(employees.get_all())

        print("\nDB-API search (Sales):")
        for row in find_employees_by_department(DATABASE_PATH, "Sales"):
            print(" ", row)

        print(f"\nAverage salary: {service.average_salary():.2f}")
        best = service.highest_paid()
        if best is not None:
            print(f"Highest salary: {best.name} {best.salary:.2f}")
        print(f"Total payroll: {service.total_payroll():.2f}")

        print("\nPayroll by department:")
        for row in service.payroll_by_department():
            print(
                f"  {row.department:8} employees={row.employees} "
                f"total={row.total_salary:.2f} average={row.average_salary:.2f}"
            )


if __name__ == "__main__":
    main()