# -*- coding: utf-8 -*-
from pathlib import Path
import typer


APP_NAME = "wusa"
WUSA_BASE_DIR = Path(typer.get_app_dir(APP_NAME, roaming=False, force_posix=True))
# Makes sure WUSA config directory exists
WUSA_BASE_DIR.mkdir(parents=True, exist_ok=True)
WUSA_RUNNER_FILE = WUSA_BASE_DIR / "runner.json"
WUSA_CLIENT_ID = "070dcc7e8ff3a7c087d5"
