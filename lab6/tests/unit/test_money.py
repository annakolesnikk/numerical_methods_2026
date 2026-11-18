import pytest

from domain_app.value_objects import Money


@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(0, id="minimum"),
        pytest.param(0.01, id="just-above-minimum"),
        pytest.param(42_000, id="typical"),
        pytest.param(1_000_000, id="large"),
    ],
)
def test_valid_money_amounts(amount: float) -> None:
    assert Money(amount).amount == pytest.approx(amount)


@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(-0.01, id="just-below-minimum"),
        pytest.param(-100, id="negative"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="infinity"),
    ],
)
def test_invalid_money_amount_raises_value_error(amount: float) -> None:
    with pytest.raises(ValueError):
        Money(amount)


def test_negative_money_error_message() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        Money(-1)


def test_money_addition_uses_float_safe_comparison() -> None:
    result = Money(0.1) + Money(0.2)

    assert result.amount == pytest.approx(0.3)
    assert result.currency == "UAH"


def test_money_addition_with_different_currency_raises() -> None:
    with pytest.raises(ValueError, match="Currency mismatch"):
        Money(100, "UAH") + Money(100, "USD")


def test_money_string_representation() -> None:
    assert str(Money(1234.5)) == "1234.50 UAH"