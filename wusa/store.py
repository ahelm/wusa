# -*- coding: utf-8 -*-
import json
from contextlib import contextmanager
from typing import Dict
from typing import Iterator

from wusa import WUSA_RUNNER_FILE


@contextmanager
def open_runners_file() -> Iterator[Dict[str, str]]:
    runner_dict = json.loads(WUSA_RUNNER_FILE.read_text())
    yield runner_dict
    WUSA_RUNNER_FILE.write_text(json.dumps(runner_dict))


def read_runners_file() -> Dict[str, str]:
    return json.loads(WUSA_RUNNER_FILE.read_text())
