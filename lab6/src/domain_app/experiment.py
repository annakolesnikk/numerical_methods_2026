from typing import Protocol

from domain_app.protocols import (
    Notifier,
)
from domain_app.services import (
    ConsoleNotifier,
)


class PayrollAlertServiceA:

    def __init__(
        self,
    ) -> None:

        self.notifier = ConsoleNotifier()

    def alert(
        self,
        recipient: str,
    ) -> None:

        self.notifier.send(
            recipient,
            "Payroll is ready",
        )


class PayrollAlertServiceB:

    def __init__(
        self,
        notifier: Notifier,
    ) -> None:

        self.notifier = notifier

    def alert(
        self,
        recipient: str,
    ) -> None:

        self.notifier.send(
            recipient,
            "Payroll is ready",
        )


class RecordingNotifier:

    def __init__(
        self,
    ) -> None:

        self.messages: list[
            tuple[str, str]
        ] = []

    def send(
        self,
        recipient: str,
        message: str,
    ) -> None:

        self.messages.append(
            (recipient, message)
        )


class BaseProcessor:

    def process(
        self,
        lines: list[str],
    ) -> list[str]:

        result = []

        for line in lines:
            fields = self.parse(line)

            if self.validate(fields):
                result.append(
                    self.format(fields)
                )

        return result

    def parse(
        self,
        line: str,
    ) -> list[str]:

        return line.split()

    def validate(
        self,
        fields: list[str],
    ) -> bool:

        return len(fields) == 2

    def format(
        self,
        fields: list[str],
    ) -> str:

        return f"{fields[0]}: {fields[1]}"


class CsvProcessor(
    BaseProcessor
):

    def parse(
        self,
        line: str,
    ) -> list[str]:

        return line.split(",")


class Parser(Protocol):

    def parse(
        self,
        line: str,
    ) -> list[str]:
        ...


class Validator(Protocol):

    def validate(
        self,
        fields: list[str],
    ) -> bool:
        ...


class Formatter(Protocol):

    def format(
        self,
        fields: list[str],
    ) -> str:
        ...


class CsvParser:

    def parse(
        self,
        line: str,
    ) -> list[str]:

        return line.split(",")


class SalaryValidator:

    def validate(
        self,
        fields: list[str],
    ) -> bool:

        return (
            len(fields) == 2
            and fields[1].isdigit()
        )


class ColonFormatter:

    def format(
        self,
        fields: list[str],
    ) -> str:

        return f"{fields[0]}: {fields[1]}"


class Processor:

    def __init__(
        self,
        parser: Parser,
        validator: Validator,
        formatter: Formatter,
    ) -> None:

        self.parser = parser
        self.validator = validator
        self.formatter = formatter

    def process(
        self,
        lines: list[str],
    ) -> list[str]:

        result = []

        for line in lines:
            fields = self.parser.parse(line)

            if self.validator.validate(fields):
                result.append(
                    self.formatter.format(fields)
                )

        return result


def main() -> None:

    print("Variant A (service creates dependency):")

    PayrollAlertServiceA().alert(
        "hr@example.com"
    )

    print("\nVariant B (dependency injection):")

    PayrollAlertServiceB(
        ConsoleNotifier()
    ).alert(
        "hr@example.com"
    )

    recorder = RecordingNotifier()

    PayrollAlertServiceB(
        recorder
    ).alert(
        "test@example.com"
    )

    print(
        "Variant B with test notifier:",
        recorder.messages,
    )

    lines = [
        "Anna Kolesnik,42000",
        "Oleh Ivanenko,65000",
        "Invalid line",
        "Iryna Petrenko,abc",
    ]

    print("\nInheritance (CsvProcessor):")
    print(CsvProcessor().process(lines))

    print("\nComposition (Processor):")
    print(
        Processor(
            parser=CsvParser(),
            validator=SalaryValidator(),
            formatter=ColonFormatter(),
        ).process(lines)
    )


if __name__ == "__main__":
    main()