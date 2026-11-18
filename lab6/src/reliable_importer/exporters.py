import json
from collections.abc import Iterable
from pathlib import Path

from reliable_importer.exceptions import DataExportError
from reliable_importer.models import Employee


def export_employees_json(employees: Iterable[Employee], path: Path) -> int:
    temporary = path.with_suffix(path.suffix + ".tmp")
    count = 0

    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        with temporary.open("w", encoding="utf-8") as file:
            file.write("[\n")
            first = True

            for employee in employees:
                if not first:
                    file.write(",\n")
                json.dump(employee.to_dict(), file, ensure_ascii=False, indent=2)
                first = False
                count += 1

            file.write("\n]\n")

        temporary.replace(path)
    except (OSError, TypeError) as error:
        temporary.unlink(missing_ok=True)
        raise DataExportError(f"Cannot export data to {path}") from error
    except BaseException:
        # Validation error in strict mode, Ctrl+C, etc. - do not leave .tmp
        temporary.unlink(missing_ok=True)
        raise

    return count