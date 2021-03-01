# -*- coding: utf-8 -*-
from pathlib import Path
import typer


APP_NAME = "wusa"
WUSA_BASE_DIR = Path(typer.get_app_dir(APP_NAME, roaming=False, force_posix=True))
WUSA_BASE_DIR.mkdir(parents=True, exist_ok=True)
