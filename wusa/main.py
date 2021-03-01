# -*- coding: utf-8 -*-
import webbrowser
from datetime import timedelta
from time import sleep

import typer

from .exceptions import BadRequest
from .exceptions import DockerError
from .exceptions import GHError
from .exceptions import InvalidRunnerName
from .exceptions import NoAccessToken
from .exceptions import PendingError
from .exceptions import RunnerFileIOError
from .gh import api_runner_list
from .gh import api_runner_registration
from .gh import get_gh_access_token
from .gh import get_gh_api
from .gh import get_gh_verification_codes
from .gh import post_gh_api
from .gh import save_access_token
from .output import press_enter_to
from .output import print_error
from .output import print_runners
from .output import print_step
from .output import status
from .runners import Runner
from .runners import Runners

app = typer.Typer()


@app.command()
def create(repo: str):
    # Task 1: Get registration token
    with status(
        "Obtaining registration token for runner",
        on_success="Token for runner registration obtained",
    ):
        try:
            runner_registration = post_gh_api(api_runner_registration(repo))
        except NoAccessToken:
            print_error("Please run 'wusa auth' to authenticate")
            raise typer.Exit(-1)
        except BadRequest as exc:
            print_error("Issue obtaining 'registration-token'")
            print_error(exc)
            raise typer.Exit(1)

    # Task 2: Create new runner
    with status(
        "Creating new runner",
        on_success="New runner created",
    ):
        try:
            new_runner = Runners.create_new_runner(
                repo,
                str(runner_registration["token"]),
            )
        except DockerError as exc:
            print_error("During runner creation an error occurred")
            print_error(exc)
            raise typer.Exit(2)
        except RunnerFileIOError as exc:
            print_error("An issue with the runner config file occurred")
            print_error(exc)
            raise typer.Exit(2)

    with status(
        "Starting up new runner",
        on_success=f"Runner '{new_runner.name}' is up and running",
    ):
        try:
            new_runner.up()
        except DockerError as exc:
            print_error("An error occurred during runner startup")
            print_error(exc)
            raise typer.Exit(3)


@app.command(name="list-local")
def list_local_runners():
    print_runners(Runners)


@app.command(name="remove")
def remove_runner(runner_name: str):
    with status(
        "Removing wusa runner",
        on_success=f"Runner '{runner_name}' successfully removed",
    ):
        try:
            Runners.remove(runner_name)
        except InvalidRunnerName as exc:
            print_error("An error occurred while trying to remove a runner")
            print_error(exc)
            raise typer.Exit(-2)
        except NoAccessToken:
            print_error("Please run 'wusa auth' to authenticate")
            raise typer.Exit(-1)
        except BadRequest as exc:
            print_error("Issue obtaining 'removal-token'")
            print_error(exc)
            raise typer.Exit(1)


@app.command(name="list-repo")
def list_repo_runners(repo: str):
    try:
        response = get_gh_api(api_runner_list(repo))
        repo_runners = response["runners"]
        repo_runners_as_runners = [Runner.from_dict(repo, r) for r in repo_runners]
        print_runners(repo_runners_as_runners, with_repo_column=False)
    except NoAccessToken:
        print_error("Please run 'wusa auth' to authenticate")
        raise typer.Exit(-1)
    except BadRequest as exc:
        print_error("Issue obtaining runner information")
        print_error(exc)
        raise typer.Exit(1)


@app.command(short_help="Login or refresh your authentication")
def auth():
    try:
        verification_response = get_gh_verification_codes()
    except GHError as exc:
        print_error("An error occurred while trying to obtain device code")
        print_error(exc)
        raise typer.Exit(1)

    code = verification_response["user_code"]
    url = verification_response["verification_uri"]
    expires_in = verification_response["expires_in"]
    interval = verification_response["interval"]
    device_code = verification_response["device_code"]

    print_step(f"Use the following verification code: [bold]{code}[/bold]")

    if press_enter_to(f"open '{url}'"):
        webbrowser.open(url)

    with status(
        "Waiting for device verification",
        on_success="Successfully obtained token",
    ):
        time_until_expiration = timedelta(seconds=expires_in)
        time_between_requests = timedelta(seconds=interval)
        number_checks = time_until_expiration // time_between_requests

        for _ in range(number_checks):
            try:
                access_token = get_gh_access_token(device_code)
                break
            except PendingError:
                sleep(time_between_requests.seconds)
            except GHError as exc:
                print_error("An error occurred while trying to obtain access token")
                print_error(exc)
                raise typer.Exit(2)

    save_access_token(access_token)
