from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from employee_manager.models import Department, Employee


@dataclass(frozen=True)
class DepartmentPayroll:
    department: str
    employees: int
    total_salary: float
    average_salary: float


class EmployeeService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def average_salary(self, department_id: int | None = None) -> float:
        statement = select(func.avg(Employee.salary))
        if department_id is not None:
            statement = statement.where(Employee.department_id == department_id)
        result = self.session.scalar(statement)
        return 0.0 if result is None else float(result)

    def highest_paid(self) -> Employee | None:
        statement = select(Employee).order_by(Employee.salary.desc()).limit(1)
        return self.session.scalar(statement)

    def total_payroll(self) -> float:
        result = self.session.scalar(select(func.sum(Employee.salary)))
        return 0.0 if result is None else float(result)

    def payroll_by_department(self) -> list[DepartmentPayroll]:
        statement = (
            select(
                Department.name,
                func.count(Employee.id),
                func.sum(Employee.salary),
                func.avg(Employee.salary),
            )
            .join(Employee, Employee.department_id == Department.id)
            .group_by(Department.name)
            .order_by(Department.name)
        )
        return [
            DepartmentPayroll(name, count, float(total), float(average))
            for name, count, total, average in self.session.execute(statement)
        ]


def transfer_employees(
    session: Session,
    employee_ids: list[int],
    new_department_id: int,
) -> None:
    try:
        if session.get(Department, new_department_id) is None:
            raise ValueError("Department not found")

        for employee_id in employee_ids:
            employee = session.get(Employee, employee_id)
            if employee is None:
                raise ValueError(f"Employee {employee_id} not found")
            employee.department_id = new_department_id

        session.commit()
    except Exception:
        session.rollback()
        raise