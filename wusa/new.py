# -*- coding: utf-8 -*-
# import uuid
from pathlib import Path
from typing import List
from typing import Protocol

from docker.types import Mount

import wusa


class NewNamespace(Protocol):
    repo: str
    token: str
    dir: Path
    labels: List[str]


def new(namespace: NewNamespace):
    """New subcommand"""
    container = wusa.CLIENT.containers.run(
        "myoung34/github-runner:latest",
        detach=True,
        remove=True,
        environment=[
            "REPO_URL=https://github.com/ahelm/wusa",
            "RUNNER_NAME=github-runner",
            "RUNNER_TOKEN=AAKKMGVJR7EWNA6DSHMDBRC74ZF3I",
            "RUNNER_WORKDIR=/Users/anton/Source/wusa/tmp",
        ],
        mounts=[
            Mount(
                "/var/run/docker.sock",
                "/var/run/docker.sock",
                type="bind",
            ),
            Mount(
                "/Users/anton/Source/wusa/tmp",
                "/Users/anton/Source/wusa/tmp",
                type="bind",
            ),
        ],
    )
    for line in container.logs(follow=True, stream=True):
        print(line.strip().decode())
    container.remove()
