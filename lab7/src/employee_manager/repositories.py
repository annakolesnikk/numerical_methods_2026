from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from employee_manager.models import Department, Employee


class DepartmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, name: str) -> Department:
        department = Department(name=name)
        self.session.add(department)
        self._commit()
        self.session.refresh(department)
        return department

    def get_by_id(self, department_id: int) -> Department | None:
        return self.session.get(Department, department_id)

    def get_by_name(self, name: str) -> Department | None:
        statement = select(Department).where(Department.name == name)
        return self.session.scalar(statement)

    def get_all(self) -> list[Department]:
        statement = select(Department).order_by(Department.name)
        return list(self.session.scalars(statement))

    def rename(self, department_id: int, new_name: str) -> Department | None:
        department = self.get_by_id(department_id)
        if department is None:
            return None
        department.name = new_name
        self._commit()
        return department

    def delete(self, department_id: int) -> bool:
        department = self.get_by_id(department_id)
        if department is None:
            return False
        self.session.delete(department)
        self._commit()
        return True

    def _commit(self) -> None:
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise


class EmployeeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, employee: Employee) -> Employee:
        self.session.add(employee)
        self._commit()
        self.session.refresh(employee)
        return employee

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self.session.get(Employee, employee_id)

    def get_all(self) -> list[Employee]:
        statement = select(Employee).order_by(Employee.id)
        return list(self.session.scalars(statement))

    def find_by_department(self, department_name: str) -> list[Employee]:
        statement = (
            select(Employee)
            .join(Department, Employee.department_id == Department.id)
            .where(Department.name == department_name)
            .order_by(Employee.name)
        )
        return list(self.session.scalars(statement))

    def update_position(self, employee_id: int, position: str) -> Employee | None:
        employee = self.get_by_id(employee_id)
        if employee is None:
            return None
        employee.position = position
        self._commit()
        return employee

    def update_salary(self, employee_id: int, salary: float) -> Employee | None:
        employee = self.get_by_id(employee_id)
        if employee is None:
            return None
        employee.salary = salary
        self._commit()
        return employee

    def delete(self, employee_id: int) -> bool:
        employee = self.get_by_id(employee_id)
        if employee is None:
            return False
        self.session.delete(employee)
        self._commit()
        return True

    def _commit(self) -> None:
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise