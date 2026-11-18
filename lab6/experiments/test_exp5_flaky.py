import random

import pytest


def pick_employee_of_month(ids: list[int]) -> int:
    return random.choice(ids)


def test_random_bad() -> None:
    assert pick_employee_of_month([1, 2]) == 1


def test_random_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(random, "choice", lambda items: items[0])

    assert pick_employee_of_month([1, 2]) == 1