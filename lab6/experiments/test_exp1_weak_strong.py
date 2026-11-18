import pytest

from bonus import bonus_amount


def test_bonus_weak() -> None:
    bonus_amount(42_000, 10)


def test_bonus_strong() -> None:
    assert bonus_amount(42_000, 10) == pytest.approx(4_200)