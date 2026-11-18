from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Sequence
from typing import Protocol

from domain_app.models import (
    PayrollRecord,
)
from domain_app.value_objects import (
    Money,
)


class ReportFormatter(
    ABC
):

    @abstractmethod
    def format(
        self,
        records: Sequence[PayrollRecord],
        total: Money,
    ) -> str:
        ...


class Notifier(
    Protocol
):

    def send(
        self,
        recipient: str,
        message: str,
    ) -> None:
        ...



class PayrollProvider(
    Protocol
):

    async def fetch_monthly_pay(
        self,
        employee_id: int,
        period: str,
    ) -> Money:
        ...        