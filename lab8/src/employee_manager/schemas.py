from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class DepartmentResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    position: str = Field(min_length=2, max_length=100)
    salary: float = Field(ge=0)
    department_id: int = Field(gt=0)


class EmployeeUpdate(BaseModel):
    position: str | None = Field(default=None, min_length=2, max_length=100)
    salary: float | None = Field(default=None, ge=0)
    department_id: int | None = Field(default=None, gt=0)


class EmployeeResponse(BaseModel):
    id: int
    name: str
    position: str
    salary: float
    department_id: int

    model_config = {"from_attributes": True}


class SalaryStatisticsResponse(BaseModel):
    employees_count: int
    average_salary: float
    max_salary: float
    total_payroll: float


class DepartmentStatisticsResponse(SalaryStatisticsResponse):
    department_id: int
    department: str