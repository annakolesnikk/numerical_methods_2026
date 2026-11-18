from __future__ import annotations

from datetime import date

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    employees: Mapped[list["Employee"]] = relationship(
        back_populates="department",
        cascade="all, delete-orphan",
    )


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint("salary >= 0", name="ck_employees_salary_non_negative"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    position: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    salary: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
    )
    hire_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    department: Mapped["Department"] = relationship(
        back_populates="employees",
    )