# -*- coding: utf-8 -*-
from contextlib import contextmanager
from typing import Generator
from typing import Optional
from typing import Union

from rich.console import Console
from rich.prompt import Confirm

CONSOLE = Console()
ERROR_CONSOLE = Console(stderr=True)


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


@contextmanager
def status(
    message: str, on_success: Optional[str] = None
) -> Generator[None, None, None]:
    with CONSOLE.status(message):
        yield
    if on_success:
        success(on_success)
