import sqlite3


def find_employees_by_department(
    database_path: str,
    department_name: str,
) -> list[tuple[str, str, float]]:
    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                employees.name,
                employees.position,
                employees.salary
            FROM employees
            JOIN departments
                ON employees.department_id = departments.id
            WHERE departments.name = ?
            ORDER BY employees.name
            """,
            (department_name,),
        )
        return cursor.fetchall()