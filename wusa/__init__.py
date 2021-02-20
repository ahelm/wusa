# -*- coding: utf-8 -*-
import sys
from pathlib import Path

import docker
from docker.errors import DockerException
import typer

try:
    CLIENT = docker.from_env()
except DockerException:
    print("[ERROR] Can't obtain docker client!", file=sys.stderr)
    print("[ERROR] Is docker deamon running?", file=sys.stderr)
    sys.exit(-1)


APP_NAME = "wusa"
WUSA_BASE_DIR = Path(typer.get_app_dir(APP_NAME, roaming=False, force_posix=True))
WUSA_CONFIG_FILE = WUSA_BASE_DIR / "config.json"
WUSA_RUNNER_FILE = WUSA_BASE_DIR / "runner.json"
WUSA_CLIENT_ID = "070dcc7e8ff3a7c087d5"
