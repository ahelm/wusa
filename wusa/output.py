# -*- coding: utf-8 -*-
from typing import Union

from rich.console import Console
from rich.prompt import Confirm
from rich.prompt import Prompt

console = Console()
error_console = Console(stderr=True, style="red")
# Simple alias -> ensures that wusa uses output to handle any CLI output
prompt = Prompt
confirm = Confirm


def silent_print(message: str) -> None:
    console.print(message, style="grey50", highlight=False)


def success(message: str) -> None:
    console.print(message, style="green")


def print_error(message: Union[str, Exception]) -> None:
    message = message if isinstance(message, str) else str(message)
    error_console.print("[bold]ERROR::[/bold] " + message)
