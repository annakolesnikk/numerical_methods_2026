from pathlib import Path

import pytest

from reliable_importer.config import load_config
from reliable_importer.exceptions import ConfigurationError
from reliable_importer.main import CONFIG_ENV, resolve_config_path


def test_load_valid_config(config_factory, csv_factory) -> None:
    source = csv_factory("1,Anna Kolesnik,Sales Manager,Sales,42000\n")

    config = load_config(config_factory(input_path=source, minimum_salary=35000))

    assert config.input_path == source
    assert config.processing.minimum_salary == pytest.approx(35_000)
    assert config.processing.skip_invalid is True
    assert config.processing.allowed_departments == {"Sales", "IT", "Finance", "HR"}
    assert config.logging.level == "INFO"


def test_missing_config_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="not found") as exc_info:
        load_config(tmp_path / "missing.yaml")

    assert isinstance(exc_info.value.__cause__, FileNotFoundError)


def test_invalid_yaml_raises(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text("input: [path: \n  : broken", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid YAML"):
        load_config(path)


def test_missing_section_raises(tmp_path: Path) -> None:
    path = tmp_path / "config.yaml"
    path.write_text("output:\n  path: out.json\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="structure") as exc_info:
        load_config(path)

    assert isinstance(exc_info.value.__cause__, KeyError)


@pytest.mark.parametrize(
    ("options", "message"),
    [
        pytest.param({"minimum_salary": -1}, "non-negative", id="negative-minimum"),
        pytest.param({"departments": "[]"}, "must not be empty", id="no-departments"),
        pytest.param({"departments": "Sales"}, "structure", id="departments-not-list"),
        pytest.param({"minimum_salary": "abc"}, "structure", id="minimum-not-number"),
    ],
)
def test_invalid_processing_values_raise(
    config_factory, csv_factory, options: dict[str, object], message: str
) -> None:
    source = csv_factory("")

    with pytest.raises(ConfigurationError, match=message):
        load_config(config_factory(input_path=source, **options))


def test_unknown_log_level_raises(config_factory, csv_factory) -> None:
    path = config_factory(input_path=csv_factory(""))
    path.write_text(
        path.read_text(encoding="utf-8").replace("level: INFO", "level: VERBOSE"),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Unknown logging level"):
        load_config(path)


def test_missing_input_file_raises(config_factory, tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="Input file not found"):
        load_config(config_factory(input_path=tmp_path / "absent.csv"))


def test_config_path_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(CONFIG_ENV, "custom.yaml")

    assert resolve_config_path(["main"]) == Path("custom.yaml")


def test_default_config_path_without_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(CONFIG_ENV, raising=False)

    assert resolve_config_path(["main"]) == Path("config.yaml")


def test_command_line_argument_has_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(CONFIG_ENV, "custom.yaml")

    assert resolve_config_path(["main", "cli.yaml"]) == Path("cli.yaml")