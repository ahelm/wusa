# -*- coding: utf-8 -*-
import json
import textwrap
import webbrowser
from datetime import timedelta
from pathlib import Path
from time import sleep

import typer
from halo import Halo

from wusa import WUSA_BASE_DIR
from wusa import WUSA_CONFIG_FILE
from wusa import WUSA_RUNNER_FILE
from wusa.auth import gh_get_user_access_token
from wusa.auth import gh_user_verification_codes
from wusa.exception import PendingError
from wusa.new import create_wusa_runner
from wusa.store import open_runners_file
from wusa.utils import generate_container_name
from wusa.utils import has_valid_config
from wusa.utils import is_valid_url

app = typer.Typer()


@app.command(short_help="Create new GitHub Action runner")
def new(
    repo_url: str = typer.Argument(
        ...,
        help="Url of the repo for the runner.",
    ),
    token: str = typer.Argument(..., help="GitHub Action runner token."),
    path: Path = typer.Argument(
        Path(),
        help="Root directory for runner.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
    labels: str = typer.Option("", help="Comma-seperated labels for the runner."),
):
    """
    wusa new - Create new GitHub Action runner

    Using the provided arguments 'REPO_URL' and 'TOKEN ', wusa registers a new runner
    and starts up the container for the runner. To obtain the token, go to the repo for
    which the runner will be created, then visit 'Settings -> Actions -> Add runner' and
    copy the token in the configuration section, e.g. ,'ABCDEFGHIJKLMNOPQRSTUVWXYZ123'.
    The 'path' argument is the root directory location, which contains the runner's
    output directory.
    """
    # valide url
    if not is_valid_url(repo_url):
        typer.secho("Invalid 'REPO_URL' provided.", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    # different spinners
    creation_spinner = Halo("Creating runner")

    with open_runners_file():
        name = generate_container_name()

        creation_spinner.start()
        create_wusa_runner()
        creation_spinner.succeed(text=f"Runner '{name}' created")


@app.command(short_help="Prints configuration information")
def config():
    """
    wusa config - Prints configuration information
    """
    msg = f"""
    WUSA configuration info
    =======================

    Config file: {WUSA_CONFIG_FILE}
    Runner file: {WUSA_RUNNER_FILE}
    """
    typer.secho(textwrap.dedent(msg))


@app.command(short_help="Login or refresh your authentication")
def auth():
    """
    wusa auth - Login or refresh your authentication
    """
    user_name = typer.prompt("* GitHub username")

    try:
        codes_resp = gh_user_verification_codes()
    except ConnectionError:
        raise typer.Exit(2)

    typer.echo(
        "* Copy the verification code: '"
        + typer.style(codes_resp["user_code"], bold=True)
        + "'"
    )

    if typer.confirm(
        f"* Press Enter to open '{codes_resp['verification_uri']}' ...",
        default=True,
        show_default=False,
        prompt_suffix=" ",
    ):
        webbrowser.open(codes_resp["verification_uri"])

    with Halo(text="Waiting for device verification") as spinner:
        time_until_expiration = timedelta(seconds=codes_resp["expires_in"])
        time_between_requests = timedelta(seconds=codes_resp["interval"])
        number_checks = time_until_expiration // time_between_requests

        for _ in range(number_checks):
            try:
                user_access_token = gh_get_user_access_token(codes_resp["device_code"])
                break
            except PendingError:
                sleep(time_between_requests.seconds)
            except ConnectionError:
                raise NotImplementedError

        spinner.succeed("Obtained user access token!")

    config = {
        "username": user_name,
        "access_token": user_access_token,
    }
    WUSA_CONFIG_FILE.write_text(json.dumps(config))
    typer.echo(
        typer.style("\u2713", fg=typer.colors.GREEN, bold=True)
        + " Authentication saved"
    )


@app.callback()
def main():
    """
    Wusa - CLI for managing docker-based self-hosted runner for GitHub actions
    ==========================================================================

    It will create an docker container and register it with a repository so that actions
    for this repo can be run on a machine. Wusa helps you to manage this containers by
    providing simple commands, e.g. 'new'.
    """
    if not WUSA_BASE_DIR.exists():
        WUSA_BASE_DIR.mkdir(parents=True)

    if not WUSA_CONFIG_FILE.exists():
        WUSA_CONFIG_FILE.write_text(json.dumps({}))

    if not WUSA_RUNNER_FILE.exists():
        WUSA_RUNNER_FILE.write_text(json.dumps({}))

    if not has_valid_config():
        typer.secho(
            "ERROR :: Configuration file is invalid! Please run: "
            + typer.style("wusa auth", fg=typer.colors.RESET),
            fg=typer.colors.RED,
            bold=True,
            err=True,
        )
        raise typer.Exit(1)
