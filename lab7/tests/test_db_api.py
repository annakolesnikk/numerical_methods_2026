from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from employee_manager.db_api import find_employees_by_department
from employee_manager.models import Base, Department, Employee


def create_file_database(path) -> None:
    engine = create_engine(f"sqlite:///{path}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        it = Department(name="IT")
        session.add(it)
        session.flush()
        session.add_all(
            [
                Employee(name="Oleh Ivanenko", position="Backend Developer", salary=65_000, department_id=it.id),
                Employee(name="Andrii Shevchenko", position="Frontend Developer", salary=52_000, department_id=it.id),
            ]
        )
        session.commit()
    engine.dispose()


def test_find_employees_by_department(tmp_path) -> None:
    database = tmp_path / "test_employees.db"
    create_file_database(database)

    rows = find_employees_by_department(str(database), "IT")

    assert rows == [
        ("Andrii Shevchenko", "Frontend Developer", 52_000.0),
        ("Oleh Ivanenko", "Backend Developer", 65_000.0),
    ]


def test_parameterized_query_blocks_sql_injection(tmp_path) -> None:
    database = tmp_path / "test_employees.db"
    create_file_database(database)

    rows = find_employees_by_department(str(database), "IT' OR '1'='1")

    assert rows == []