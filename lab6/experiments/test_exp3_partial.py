from classifier import classify_salary


def test_high_salary() -> None:
    assert classify_salary(65_000) == "high"


def test_medium_salary() -> None:
    assert classify_salary(40_000) == "medium"