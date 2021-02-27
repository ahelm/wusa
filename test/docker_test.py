# -*- coding: utf-8 -*-
from docker.errors import DockerException
from pytest import raises

from wusa.docker import get_client
from wusa.exceptions import NoDockerServerFound


def test_get_client(monkeypatch):
    """Check that get_client uses 'from_env' interface to get DockerClient"""

    def mocked_from_env():
        return "success"

    monkeypatch.setattr("wusa.docker.from_env", mocked_from_env)
    assert get_client() == "success"


def test_get_client_raises_NoClient(monkeypatch):
    """Check if get_client raises 'NoDockerServerFound' exception"""

    def raises_DockerException():
        raise DockerException

    monkeypatch.setattr("wusa.docker.from_env", raises_DockerException)

    with raises(NoDockerServerFound, match="failed to connect to docker"):
        get_client()
