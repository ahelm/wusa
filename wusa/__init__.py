# -*- coding: utf-8 -*-
import sys
from pathlib import Path

import docker
from docker.errors import DockerException
import typer

try:
    wusa_client = docker.from_env()
except DockerException:
    print("[ERROR] Can't obtain docker client!", file=sys.stderr)
    print("[ERROR] Is docker deamon running?", file=sys.stderr)
    sys.exit(-1)


APP_NAME = "wusa"
WUSA_BASE_DIR = Path(typer.get_app_dir(APP_NAME, roaming=False, force_posix=True))
# Makes sure WUSA config directory exists
WUSA_BASE_DIR.mkdir(parents=True, exist_ok=True)
WUSA_ACCESS_TOKEN = WUSA_BASE_DIR / ".access_token"
WUSA_RUNNER_FILE = WUSA_BASE_DIR / "runner.json"
WUSA_CLIENT_ID = "070dcc7e8ff3a7c087d5"
