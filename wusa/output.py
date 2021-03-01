# -*- coding: utf-8 -*-
from contextlib import contextmanager
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional
from typing import Protocol
from typing import Union

from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

CONSOLE = Console()
ERROR_CONSOLE = Console(stderr=True)


class RunnerObject(Protocol):
    name: str
    repo: str
    labels: List[str]


def press_enter_to(message: str) -> bool:
    confirm = Confirm.ask(
        "[bold]*[/bold] Press Enter to " + message,
        show_choices=False,
        show_default=False,
        choices=[""],
    )
    return confirm


def print_step(message: str) -> None:
    CONSOLE.print("[bold]*[/bold] " + message)


def silent_print(message: str) -> None:
    CONSOLE.print("  " + message, style="grey50", highlight=False)


def success(message: str) -> None:
    CONSOLE.print("[bold green]\u2713[/bold green] " + message)


def print_error(message: Union[str, Exception]) -> None:
    message = message if isinstance(message, str) else str(message)
    ERROR_CONSOLE.print("[bold white on red] ERROR [/bold white on red] " + message)


def print_runners(runners: Iterable[RunnerObject]) -> None:
    table = Table()

    table.add_column("Runner name", style="bold blue", no_wrap=True)
    table.add_column("Repository", style="magenta")
    table.add_column("Labels")

    for runner in runners:
        table.add_row(runner.name, runner.repo, ",".join(runner.labels))

    CONSOLE.print(table)


@contextmanager
def status(
    message: str, on_success: Optional[str] = None
) -> Generator[None, None, None]:
    with CONSOLE.status(message):
        yield
    if on_success:
        success(on_success)
