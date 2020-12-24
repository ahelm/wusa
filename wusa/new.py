# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List
from typing import Protocol


class NewNamespace(Protocol):
    repo: str
    token: str
    dir: Path
    labels: List[str]


def new(namespace: NewNamespace):
    """New subcommand"""
    pass
