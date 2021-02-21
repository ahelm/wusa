# -*- coding: utf-8 -*-
import json
from json.decoder import JSONDecodeError

import typer
from shortuuid import ShortUUID
from validators import url

from wusa import WUSA_CONFIG_FILE
from wusa.store import read_runners_file


def is_valid_url(url_to_check: str) -> bool:
    """URL validator

    Checks if a string is a valid url.

    Parameters
    ----------
    url_to_check : str
        String to check.

    Returns
    -------
    bool
        `True` if the passed string is a valid URL
    """
    return url(url_to_check) is True


def generate_container_name() -> str:
    """Runner name generator

    Creates a string which represents a valid name for a wusa runner. The string is a
    combination of the string ``wusa_`` and an uuid of length 8. The runner name should
    be unique, but name clashes can occur. To achieve uniqueness, the function tries to
    generate up to 100 times an unique name and if it fails, the CLI is exited with an
    error.

    Returns
    -------
    str
        String of a valid wusa runner name
    """
    runners = read_runners_file()

    for _ in range(100):
        runner_name = "wusa_" + ShortUUID().random(length=8)

        if runner_name not in runners:
            return runner_name

    typer.secho("Failed to generate unique runner name!", fg=typer.colors.RED, err=True)
    raise typer.Exit(-1)


def has_valid_config() -> bool:
    try:
        json.loads(WUSA_CONFIG_FILE.read_text())
        return True
    except JSONDecodeError:
        return False


def print_error(msg: str) -> None:
    typer.secho(f"ERROR :: {msg}", fg=typer.colors.RED, err=True)


def is_valid_status_code(status_code: int, extra_msg_if_not_valid: str = "") -> bool:
    if status_code != 200:
        print_error(f"Unexpected status code '{status_code}' received!")
        if extra_msg_if_not_valid:
            print_error(extra_msg_if_not_valid)

    return status_code == 200
