from uuid import uuid4
from importlib.metadata import version
import json

import click
from click.decorators import option
import keyring

import wusa
from wusa.utils import requires_config_file


@click.group()
def main():
    pass


@main.command()
@click.argument("token", type=click.STRING, metavar="<token>")
@click.argument(
    "basedir",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
    ),
    metavar="<basedir>",
)
def init(token, basedir):
    """Initializes wusa and creates configuration files.

    Wusa uses personal access token (PAT) from Github to manage a self-hosted
    workflow runner. How to create a PAT can be found on:

    \b
    https://docs.github.com/github/authenticating-to-github/creating-a-personal-access-token

    After creation, use the `<token>` argument to pass the token to init. Tokens are
    stored in an OS-specific keyring service. Wusa also requires a base directory
    `<basedir>` for storing the output of the different runners.
    """
    keyring.set_password(wusa.WUSA_SERVICE_NAME, wusa.WUSA_USERNAME, token)

    if not wusa.WUSA_CONFIG_DIR.exists():
        wusa.WUSA_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(wusa.WUSA_CONFIG_FILE, mode="w") as fp:
        json.dump({"base_dir": basedir}, fp)

    # store in config file:
    #  [x] working directory
    #  [ ] default labels


@main.command()
@requires_config_file
def new():
    # """Creates a new runner."""
    pass
    # container_id = str(uuid4())[:8]

    # print("> creating container")
    # container = CLIENT.containers.run(
    #     "myoung34/github-runner:latest",
    #     name=f"wusa_{container_id}",
    #     environment={
    #         "REPO_URL": url,
    #         "RUNNER_TOKEN": token,
    #         "RUNNER_NAME": f"wusa_{container_id}",
    #         "RUNNER_WORKDIR": f"/tmp/wusa_{container_id}",
    #         "RUNNER_GROUP": "wusa-self-hosted",
    #     },
    #     volumes={
    #         "/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"},
    #         f"/tmp/wusa_{container_id}": {
    #             "bind": f"/tmp/wusa_{container_id}",
    #             "mode": "rw",
    #         },
    #     },
    #     labels={
    #         "wusa.version": version("wusa"),
    #         # "wusa.runner": "TRUE",
    #     },
    #     detach=True,
    # )

    # print(f"> started: {container.name} ({container.short_id})")
