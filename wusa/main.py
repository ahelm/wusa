# -*- coding: utf-8 -*-
import json
import webbrowser
from datetime import timedelta
from time import sleep

import typer

from . import WUSA_ACCESS_TOKEN
from . import WUSA_BASE_DIR
from . import WUSA_RUNNER_FILE
from .auth import gh_get_user_access_token
from .auth import gh_user_verification_codes
from .exceptions import BadRequest
from .exceptions import DockerError
from .exceptions import PendingError
from .exceptions import RunnerFileIOError
from .gh_api import post_gh_api
from .output import confirm
from .output import console
from .output import print_error
from .output import success
from .runners import Runners

app = typer.Typer()


@app.command()
def create(repo: str):
    # Task 1: Get registration token
    with console.status("Obtaining registration token for runner"):
        try:
            runner_registration = post_gh_api(
                f"/repos/{repo}/actions/runners/registration-token"
            )
        except BadRequest:
            typer.secho(
                "Issue obtaining 'registration-token'",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(2)
    success("Token for runner registration obtained")

    # Task 2: Create new runner
    with console.status("Creating new runner"):
        try:
            new_runner = Runners.create_new_runner(repo, runner_registration["token"])
        except DockerError as exc:
            print_error("During runner creation an error occurred")
            print_error(exc)
            raise typer.Exit(-2)
        except RunnerFileIOError as exc:
            print_error("An issue with the runner config file occurred")
            print_error(exc)
            raise typer.Exit(-2)

    success(f"Runner '[bold white]{new_runner.name}[/bold white]' created")

    # Task 3: Startup of runner
    with console.status("Starting up new runner"):
        try:
            new_runner.up()
        except DockerError as exc:
            print_error("An error occurred during runner startup")
            print_error(exc)
            raise typer.Exit(-2)

    success(f"Runner '[bold white]{new_runner.name}[/bold white]' is up and running")


@app.command(short_help="Login or refresh your authentication")
def auth():
    try:
        verification_response = gh_user_verification_codes()
    except ConnectionError:
        raise typer.Exit(2)

    code = verification_response["user_code"]
    url = verification_response["verification_uri"]

    console.print(f"* Use the following verification code: [bold]{code}[/bold]")

    if confirm.ask(
        f"* Press Enter to open '{url}'",
        show_choices=False,
        show_default=False,
        choices=[""],
    ):
        webbrowser.open(url)

    with console.status("Waiting for device verification"):
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

    WUSA_ACCESS_TOKEN.write_text(access_token)
    success("Obtained user access token")


@app.callback()
def main():
    if not WUSA_BASE_DIR.exists():
        WUSA_BASE_DIR.mkdir(parents=True)

    if not WUSA_RUNNER_FILE.exists():
        WUSA_RUNNER_FILE.write_text(json.dumps([]))
