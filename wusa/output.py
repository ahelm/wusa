# -*- coding: utf-8 -*-
from rich.console import Console

console = Console()


def silent_print(message: str) -> None:
    console.print(message, style="grey50", highlight=False)


def success(message: str) -> None:
    console.print(message, style="green")
