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
    status: str
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
    CONSOLE.print("[bold]*[/bold] " + message, highlight=False)


def silent_print(message: str) -> None:
    CONSOLE.print("  " + message, style="grey50", highlight=False)


def success(message: str) -> None:
    CONSOLE.print("[bold green]\u2713[/bold green] " + message, highlight=False)


def print_error(message: Union[str, Exception]) -> None:
    message = message if isinstance(message, str) else str(message)
    ERROR_CONSOLE.print(
        "[bold white on red] ERROR [/bold white on red] " + message,
        highlight=False,
    )


def print_runners(
    runners: Iterable[RunnerObject],
    with_repo_column: bool = True,
) -> None:
    table = Table()

    table.add_column("Runner name", style="bold blue", no_wrap=True)
    if with_repo_column:
        table.add_column("Repository", style="magenta")
    table.add_column("Status")
    table.add_column("Labels")

    for runner in runners:
        runner_status = runner.status
        if runner_status in ["online", "idle"]:
            runner_status = "[green]" + runner_status + "[/green]"
        else:
            runner_status = "[grey50]" + runner_status + "[/grey50]"

        args = [runner.name]

        if with_repo_column:
            args += [runner.repo]

        args += [runner_status, ", ".join(runner.labels)]
        table.add_row(*args)

    CONSOLE.print(table)


@contextmanager
def status(
    message: str, on_success: Optional[str] = None
) -> Generator[None, None, None]:
    with CONSOLE.status(message):
        yield
    if on_success:
        success(on_success)
