from pathlib import Path
import sys

from click import secho
import docker
import appdirs
from docker.models.configs import ConfigCollection

try:
    CLIENT = docker.from_env()
except docker.errors.DockerException as e:
    secho("[ERROR] Can't obtain docker client!", fg="red", err=True)
    secho("[ERROR] Is docker deamon running?", fg="red", err=True)
    sys.exit(-1)


WUSA_CONFIG_DIR = Path(appdirs.user_config_dir(appname="wusa"))
WUSA_CONFIG_FILE = WUSA_CONFIG_DIR / "config.json"
WUSA_SERVICE_NAME = "wusa.cli"
WUSA_USERNAME = "wusa-runner"
