import math
from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class Money:
    amount: float
    currency: str = "UAH"

    def __post_init__(
        self,
    ) -> None:

        if not math.isfinite(
            self.amount
        ):
            raise ValueError(
                "Money amount "
                "must be a finite number"
            )

        if self.amount < 0:
            raise ValueError(
                "Money amount "
                "cannot be negative"
            )

    def __add__(
        self,
        other: "Money",
    ) -> "Money":

        if (
            self.currency
            != other.currency
        ):
            raise ValueError(
                "Currency mismatch"
            )

        return Money(
            self.amount
            + other.amount,
            self.currency,
        )

    def __str__(
        self,
    ) -> str:

        return (
            f"{self.amount:.2f} "
            f"{self.currency}"
        )