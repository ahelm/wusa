# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List
from typing import NamedTuple

import pytest

import wusa
from wusa.new import new


@pytest.fixture(name="namespace")
def _NewNamespace(tmp_path):
    class Namespace(NamedTuple):
        repo: str
        token: str
        dir: Path
        labels: List[str]

    return Namespace(
        "http://some-repo",
        "ABCD",
        tmp_path.absolute(),
        ["l1", "l2", "l3"],
    )


@pytest.fixture(name="mocked_docker")
def _patched_docker_client(monkeypatch):
    class Containers:
        def run(self, image, command=None, **kwargs):
            self.image = image
            self.command = command
            self.detach = kwargs.get("detach", None)
            self.name = kwargs.get("name", "")
            self.environment = kwargs.get("environment", {})
            self.mounts = kwargs.get("mounts", [])

    class DockerClient:
        containers = Containers()

    client = DockerClient()
    monkeypatch.setattr(wusa, "CLIENT", client)
    return client


def test_new(namespace, mocked_docker):
    new(namespace)

    container = mocked_docker.containers

    assert container.image == "myoung34/github-runner:latest"
    assert container.command is None
    assert container.detach is True
    assert container.name.startswith("wusa_")
    assert container.environment["REPO_URL"] == namespace.repo
    assert container.environment["RUNNER_TOKEN"] == namespace.token
    assert container.environment["RUNNER_WORKDIR"] == namespace.dir
    assert container.environment["RUNNER_NAME"] == container.name
    assert set(container.mounts) == {
        "/var/run/docker.sock:/var/run/docker.sock",
        f"{namespace.dir}:{namespace.dir}",
    }
