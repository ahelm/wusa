# -*- coding: utf-8 -*-
import json
import webbrowser
from datetime import timedelta
from time import sleep

import typer
from halo import Halo
from rich.console import Console

from wusa import WUSA_ACCESS_TOKEN
from wusa import WUSA_BASE_DIR
from wusa import WUSA_RUNNER_FILE
from wusa.auth import gh_get_user_access_token
from wusa.auth import gh_user_verification_codes
from wusa.exception import PendingError

app = typer.Typer()


@app.command(name="list", short_help="List all runners")
def list_runners():
    console = Console()
    runners = json.loads(WUSA_RUNNER_FILE.read_text())
    console.print(runners)


@app.command(short_help="Login or refresh your authentication")
def auth():
    try:
        verification_response = gh_user_verification_codes()
    except ConnectionError:
        raise typer.Exit(2)

    typer.echo(
        "* Copy the verification code: '"
        + typer.style(verification_response["user_code"], bold=True)
        + "'"
    )

    if typer.confirm(
        f"* Press Enter to open '{verification_response['verification_uri']}' ...",
        default=True,
        show_default=False,
        prompt_suffix=" ",
    ):
        webbrowser.open(verification_response["verification_uri"])

    with Halo(text="Waiting for device verification") as spinner:
        time_until_expiration = timedelta(seconds=verification_response["expires_in"])
        time_between_requests = timedelta(seconds=verification_response["interval"])
        number_checks = time_until_expiration // time_between_requests

        for _ in range(number_checks):
            try:
                access_token = gh_get_user_access_token(
                    verification_response["device_code"],
                )
                break
            except PendingError:
                sleep(time_between_requests.seconds)
            except ConnectionError:
                raise NotImplementedError

        spinner.succeed("Obtained user access token!")

    WUSA_ACCESS_TOKEN.write_text(access_token)


@app.callback()
def main():
    if not WUSA_BASE_DIR.exists():
        WUSA_BASE_DIR.mkdir(parents=True)

    if not WUSA_RUNNER_FILE.exists():
        WUSA_RUNNER_FILE.write_text(json.dumps({}))
