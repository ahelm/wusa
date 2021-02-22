# -*- coding: utf-8 -*-
import typer
from shortuuid import ShortUUID
from validators import url

from wusa.store import read_runners_file


def is_valid_url(url_to_check: str) -> bool:
    return url(url_to_check) is True


def generate_container_name() -> str:
    runners = read_runners_file()

    for _ in range(100):
        runner_name = "wusa_" + ShortUUID().random(length=8)

        if runner_name not in runners:
            return runner_name

    typer.secho("Failed to generate unique runner name!", fg=typer.colors.RED, err=True)
    raise typer.Exit(-1)


def print_error(msg: str) -> None:
    typer.secho(f"ERROR :: {msg}", fg=typer.colors.RED, err=True)


def is_valid_status_code(status_code: int, api_address: str = "") -> bool:
    if status_code != 200:
        print_error(f"Response from '{api_address}' was incorrect!")
        print_error(f"Unexpected status code '{status_code}' received!")
        return False
    else:
        return True
