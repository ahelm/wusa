from pathlib import Path
import sys

import docker
import appdirs
from docker.models.configs import ConfigCollection

try:
    CLIENT = docker.from_env()
except docker.errors.DockerException as e:
    print("[ERROR] Can't obtain docker client!", file=sys.stderr)
    print("[ERROR] Is docker deamon running?", file=sys.stderr)
    sys.exit(-1)


WUSA_CONFIG_DIR = Path(appdirs.user_config_dir(appname="wusa"))
WUSA_CONFIG_FILE = WUSA_CONFIG_DIR / "config.json"
WUSA_SERVICE_NAME = "wusa.cli"
WUSA_USERNAME = "wusa-runner"
