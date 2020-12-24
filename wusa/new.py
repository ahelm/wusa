# -*- coding: utf-8 -*-
# import uuid
from pathlib import Path
from typing import List
from typing import Protocol

import wusa


class NewNamespace(Protocol):
    repo: str
    token: str
    dir: Path
    labels: List[str]


def new(namespace: NewNamespace):
    """New subcommand"""
    # print(f"Ping to client = {wusa.CLIENT.ping()}")
    # container_short_id = str(uuid.uuid4())[:8]

    # envs = {
    #     "REPO_URL": namespace.repo,
    #     "RUNNER_NAME": f"wusa_{container_short_id}",
    #     "RUNNER_TOKEN": namespace.token,
    #     "RUNNER_WORKDIR": str(namespace.dir),
    # }
    # mounts = [
    #     "/var/run/docker.sock:/var/run/docker.sock",
    #     f"{namespace.dir}:{namespace.dir}",
    # ]

    # breakpoint()
    wusa.CLIENT.containers.run("alpine", "echo hello world", remove=True)

    # wusa.CLIENT.containers.run(
    #     "myoung34/github-runner:latest",
    #     detach=True,
    #     name=envs["RUNNER_NAME"],
    #     environment=envs,
    #     mounts=mounts,
    # )


# cont = client.containers.run(
#     "myoung34/github-runner:latest",
#     detach=True,
#     name="github-runner",
#     environment=[
#         "REPO_URL=https://github.com/ahelm/wusa",
#         "RUNNER_NAME=github-runner",
#         "RUNNER_TOKEN=AAKKMGTAVI5VYNKFJENUA3274QMCQ",
#         "RUNNER_WORKDIR=/Users/anton/Documents/Projects/wusa",
#     ],
#     mounts=[
#         "/var/run/docker.sock:/var/run/docker.sock",
#         "/Users/anton/Documents/Projects/wusa:/Users/anton/Documents/Projects/wusa",
#     ],
# )
