import json
import sys

import pytest

from reliable_importer import main as app

pytestmark = pytest.mark.integration


def test_main_runs_full_application(
    monkeypatch: pytest.MonkeyPatch, tmp_path, csv_factory, config_factory
) -> None:
    source = csv_factory(
        "1,Anna Kolesnik,Sales Manager,Sales,42000\n"
        "2,Oleh Ivanenko,Backend Developer,IT,65000\n"
        "3,Taras Melnyk,Lawyer,Legal,50000\n"
    )
    config = config_factory(input_path=source, minimum_salary=50000)
    monkeypatch.setattr(sys, "argv", ["reliable-importer", str(config)])

    app.main()

    data = json.loads((tmp_path / "output" / "employees.json").read_text(encoding="utf-8"))
    log_text = (tmp_path / "logs" / "application.log").read_text(encoding="utf-8")
    assert [item["employee_id"] for item in data] == [2]
    assert "Total=3, valid=2, invalid=1, filtered=1, exported=1" in log_text
    assert "42000" not in log_text and "65000" not in log_text


def test_main_uses_config_from_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path, csv_factory, config_factory
) -> None:
    config = config_factory(input_path=csv_factory("1,Anna Kolesnik,Sales Manager,Sales,42000\n"))
    monkeypatch.setattr(sys, "argv", ["reliable-importer"])
    monkeypatch.setenv(app.CONFIG_ENV, str(config))

    app.main()

    assert (tmp_path / "output" / "employees.json").exists()


def test_main_exits_with_code_1_on_configuration_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    monkeypatch.setattr(sys, "argv", ["reliable-importer", str(tmp_path / "missing.yaml")])

    with pytest.raises(SystemExit) as exc_info:
        app.main()

    assert exc_info.value.code == 1