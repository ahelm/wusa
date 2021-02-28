# -*- coding: utf-8 -*-
from typing import Union

import typer
from validators import url


def is_valid_url(url_to_check: str) -> bool:
    return url(url_to_check) is True


def print_error(msg: Union[str, Exception]) -> None:
    typer.secho(f"ERROR :: {msg}", fg=typer.colors.RED, err=True)


def is_valid_status_code(status_code: int, api_address: str = "") -> bool:
    if status_code != 200:
        print_error(f"Response from '{api_address}' was incorrect!")
        print_error(f"Unexpected status code '{status_code}' received!")
        return False
    else:
        return True
