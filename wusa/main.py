# -*- coding: utf-8 -*-
import json
import webbrowser
from dataclasses import asdict
from dataclasses import dataclass
from datetime import timedelta
from string import ascii_lowercase
from time import sleep

import typer
from gidgethub import BadRequest
from halo import Halo
from rich.console import Console
from shortuuid import ShortUUID

from wusa import WUSA_ACCESS_TOKEN
from wusa import WUSA_BASE_DIR
from wusa import WUSA_RUNNER_FILE
from wusa import wusa_client
from wusa.auth import gh_get_user_access_token
from wusa.auth import gh_user_verification_codes
from wusa.exception import PendingError
from wusa.gh_api import post_gh_api

app = typer.Typer()


@dataclass
class Runner:
    name: str
    repo_url: str
    token: str

    @property
    def config_cmd(self) -> str:
        return (
            f"./config.sh "
            f" --unattended"
            f" --url {self.repo_url}"
            f" --name {self.name}"
            f" --replace"
            f" --token {self.token}"
        )

    def save(self) -> None:
        runners = json.loads(WUSA_RUNNER_FILE.read_text())
        runners.append(asdict(self))
        WUSA_RUNNER_FILE.write_text(json.dumps(runners))

    @classmethod
    def new(cls, repo: str, token: str) -> "Runner":
        id_ = ShortUUID(alphabet=ascii_lowercase).random(8)
        name = f"wusa-{id_}"
        repo_url = f"https://github.com/{repo}"
        return cls(name, repo_url, token)


@app.command()
def create(repo: str):
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

    new_runner = Runner.new(repo, runner_registration["token"])
    new_runner.save()

    wusa_container = wusa_client.containers.run(
        "wusarunner/base-linux:latest",
        command=new_runner.config_cmd,
        detach=True,
    )

    for line in wusa_container.logs(stream=True):
        cleaned_line = line.decode("utf-8").strip()
        if cleaned_line:
            print(cleaned_line)

    wusa_container.commit(repository=f"{new_runner.name}", tag="latest")
    wusa_container.remove()


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
        WUSA_RUNNER_FILE.write_text(json.dumps([]))
