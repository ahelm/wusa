import json

import click
import keyring

from wusa.utils import requires_config_file
import wusa


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
    """Creates a new docker based runner for a GitHub action."""
    pass
