import csv
import json
import logging
import tempfile
import traceback
import tracemalloc
from collections.abc import Iterator
from pathlib import Path
from time import perf_counter

from reliable_importer.config import load_config
from reliable_importer.exceptions import (
    ApplicationError,
    DataExportError,
    RecordValidationError,
)
from reliable_importer.exporters import export_employees_json
from reliable_importer.models import Employee
from reliable_importer.services import ImportStatistics, import_employees
from reliable_importer.validators import parse_employee

HEADER = ["employee_id", "name", "position", "department", "salary"]
DEPARTMENTS = {"Sales", "IT", "Finance", "HR"}


def generate_csv(path: Path, valid: int, invalid: int = 0) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(HEADER)
        step = valid // invalid if invalid else 0

        for index in range(1, valid + 1):
            writer.writerow(
                [index, f"Employee {index}", "Developer", "IT", 30000 + index]
            )
            if invalid and index % step == 0:
                writer.writerow(["bad", "", "", "Unknown", "-1"])


# ---------- Experiment 1: strict vs tolerant ----------

def experiment_strict_vs_tolerant(directory: Path) -> None:
    print("\n=== Experiment 1. Strict vs tolerant ===")
    source = directory / "employees_1010.csv"
    generate_csv(source, valid=1000, invalid=10)

    for mode, skip_invalid in (("Strict", False), ("Tolerant", True)):
        statistics = ImportStatistics()
        output = directory / f"{mode.lower()}.json"
        exported = 0
        result = "completed"

        try:
            exported = export_employees_json(
                import_employees(
                    source,
                    allowed_departments=DEPARTMENTS,
                    skip_invalid=skip_invalid,
                    statistics=statistics,
                ),
                output,
            )
        except ApplicationError as error:
            result = f"stopped: {type(error).__name__}"

        print(
            f"{mode:8} processed={statistics.total} valid={statistics.valid} "
            f"invalid={statistics.invalid} exported={exported} "
            f"output exists={output.exists()} -> {result}"
        )


# ---------- Experiment 2: streaming vs eager ----------

def eager_import(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def streaming_import(path: Path) -> Iterator[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as file:
        yield from csv.DictReader(file)


def measure(action: str, path: Path) -> tuple[float, int]:
    tracemalloc.start()
    start = perf_counter()

    if action == "eager":
        count = len(eager_import(path))
    else:
        count = sum(1 for _ in streaming_import(path))

    elapsed = perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert count > 0
    return elapsed, peak


def experiment_streaming_vs_eager(directory: Path) -> None:
    print("\n=== Experiment 2. Streaming vs eager ===")
    print(
        f"{'Records':>8} | {'Eager time, s':>13} | {'Streaming time, s':>17} | "
        f"{'Eager peak, MB':>14} | {'Streaming peak, MB':>18}"
    )

    for size in (10_000, 100_000, 500_000):
        source = directory / f"employees_{size}.csv"
        generate_csv(source, valid=size)

        eager_time, eager_peak = measure("eager", source)
        stream_time, stream_peak = measure("streaming", source)

        print(
            f"{size:>8} | {eager_time:>13.4f} | {stream_time:>17.4f} | "
            f"{eager_peak / 1024**2:>14.2f} | {stream_peak / 1024**2:>18.4f}"
        )


# ---------- Experiment 3: exception chaining ----------

def experiment_exception_chaining() -> None:
    print("\n=== Experiment 3. Exception chaining ===")
    row = {
        "employee_id": "1",
        "name": "Anna Kolesnik",
        "position": "Sales Manager",
        "department": "Sales",
        "salary": "wrong",
    }

    try:
        parse_employee(row, line_number=2, allowed_departments=DEPARTMENTS)
    except RecordValidationError as error:
        traceback.print_exception(error)
        print(
            f"Chain: {type(error.__cause__).__name__} -> "
            f"{type(error).__name__}"
        )


# ---------- Experiment 4: atomic output ----------

def failing_employees() -> Iterator[Employee]:
    yield Employee(1, "Anna Kolesnik", "Sales Manager", "Sales", 42000)
    raise OSError("Simulated disk failure during export")


def experiment_atomic_output(directory: Path) -> None:
    print("\n=== Experiment 4. Atomic output ===")
    output = directory / "employees.json"
    export_employees_json(
        [Employee(2, "Oleh Ivanenko", "Backend Developer", "IT", 65000)],
        output,
    )
    before = output.read_text(encoding="utf-8")

    try:
        export_employees_json(failing_employees(), output)
    except DataExportError as error:
        print(f"Caught: {type(error).__name__}: {error}")
        print(f"Cause:  {type(error.__cause__).__name__}: {error.__cause__}")

    print("Previous output unchanged:", output.read_text(encoding="utf-8") == before)
    print("Output is valid JSON:", isinstance(json.loads(before), list))
    print("Temporary file removed:", not output.with_suffix(".json.tmp").exists())


# ---------- Experiment 5: configuration errors ----------

VALID_CONFIG = """\
input:
  path: {input}
output:
  path: {output}
processing:
  minimum_salary: {minimum}
  skip_invalid: true
  allowed_departments: [Sales, IT, Finance, HR]
logging:
  level: INFO
  path: logs/application.log
"""


def experiment_configuration_errors(directory: Path) -> None:
    print("\n=== Experiment 5. Configuration errors ===")
    source = directory / "employees.csv"
    generate_csv(source, valid=5)

    cases = {
        "1. Missing config.yaml": None,
        "2. Invalid YAML": "input: [path: \n  : broken",
        "3. No 'input' key": VALID_CONFIG.format(
            input=source, output=directory / "out.json", minimum=30000
        ).replace("input:\n", "source:\n", 1),
        "4. minimum_salary = -500": VALID_CONFIG.format(
            input=source, output=directory / "out.json", minimum=-500
        ),
        "5. Input file missing": VALID_CONFIG.format(
            input=directory / "missing.csv", output=directory / "out.json",
            minimum=30000,
        ),
        "6. Output directory missing": VALID_CONFIG.format(
            input=source, output=directory / "new_dir" / "out.json",
            minimum=30000,
        ),
    }

    for title, text in cases.items():
        path = directory / f"config_{title[0]}.yaml"
        if text is not None:
            path.write_text(text, encoding="utf-8")

        try:
            config = load_config(path)
            statistics = ImportStatistics()
            exported = export_employees_json(
                import_employees(
                    config.input_path,
                    allowed_departments=config.processing.allowed_departments,
                    skip_invalid=True,
                    statistics=statistics,
                ),
                config.output_path,
            )
            print(f"{title}: OK, directory created, exported={exported}")
        except ApplicationError as error:
            cause = (
                f" (cause: {type(error.__cause__).__name__})"
                if error.__cause__ else ""
            )
            print(f"{title}: {type(error).__name__}: {error}{cause}")


def main() -> None:
    logging.disable(logging.CRITICAL)

    with tempfile.TemporaryDirectory() as name:
        directory = Path(name)
        experiment_strict_vs_tolerant(directory)
        experiment_streaming_vs_eager(directory)
        experiment_exception_chaining()
        experiment_atomic_output(directory)
        experiment_configuration_errors(directory)


if __name__ == "__main__":
    main()