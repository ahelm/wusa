from pathlib import Path

import docker
import appdirs
from docker.models.configs import ConfigCollection

CLIENT = docker.from_env()
WUSA_CONFIG_DIR = Path(appdirs.user_config_dir(appname="wusa"))
WUSA_CONFIG_FILE = WUSA_CONFIG_DIR / "config.json"
WUSA_SERVICE_NAME = "wusa.cli"
WUSA_USERNAME = "wusa-runner"
