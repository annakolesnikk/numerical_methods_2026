from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Employee:
    employee_id: int
    name: str
    position: str
    department: str
    salary: float = field(repr=False)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ProcessingConfig:
    minimum_salary: float
    skip_invalid: bool
    allowed_departments: frozenset[str]


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    level: str
    path: Path


@dataclass(frozen=True, slots=True)
class AppConfig:
    input_path: Path
    output_path: Path
    processing: ProcessingConfig
    logging: LoggingConfig