import json
from pathlib import Path

from reliable_importer.exporters import export_employees_json
from reliable_importer.models import Employee


def test_export_is_isolated(tmp_path: Path) -> None:
    output = tmp_path / "employees.json"

    export_employees_json([Employee(1, "Anna Kolesnik", "Manager", "Sales", 42000)], output)

    print(f"\ntmp_path = {tmp_path}")
    assert len(json.loads(output.read_text(encoding="utf-8"))) == 1
    assert not Path("output/employees.json").exists()