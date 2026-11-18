import pytest

from classifier import classify_salary


@pytest.mark.parametrize(
    ("amount", "expected"),
    [(65_000, "high"), (40_000, "medium"), (20_000, "low")],
)
def test_classify_salary(amount: float, expected: str) -> None:
    assert classify_salary(amount) == expected