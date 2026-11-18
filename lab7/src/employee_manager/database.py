import sqlite3

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

DATABASE_PATH = "employees.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


def enable_sqlite_foreign_keys(dbapi_connection: object, connection_record: object) -> None:
    # SQLite checks FOREIGN KEY constraints only when this pragma is on.
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


engine = create_engine(
    DATABASE_URL,
    echo=False,
)
event.listen(engine, "connect", enable_sqlite_foreign_keys)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)