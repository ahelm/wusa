# -*- coding: utf-8 -*-
import json
import textwrap
from pathlib import Path

import typer
from halo import Halo

from wusa import WUSA_BASE_DIR
from wusa import WUSA_CONFIG_FILE
from wusa import WUSA_RUNNER_FILE
from wusa.new import create_wusa_runner
from wusa.store import open_runners_file
from wusa.utils import generate_container_name
from wusa.utils import is_valid_url

app = typer.Typer()


@app.command()
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
    wusa new - creates a new wusa runner

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


@app.command(short_help="Prints configuration information.")
def config():
    """
    wusa config - prints configuration information
    """
    msg = f"""
    WUSA configuration info
    =======================

    Application directory:
        {WUSA_BASE_DIR}

    Config file:
        {WUSA_CONFIG_FILE}

    Runner file:
        {WUSA_RUNNER_FILE}
    """
    typer
    typer.secho(textwrap.dedent(msg))


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
        WUSA_CONFIG_FILE.touch()

    if not WUSA_RUNNER_FILE.exists():
        # store empty dictionary
        with WUSA_RUNNER_FILE.open("w") as fp:
            json.dump({}, fp)
