# -*- coding: utf-8 -*-
from docker.errors import APIError
from docker.errors import DockerException
from docker.errors import ImageNotFound
from pytest import fixture
from pytest import raises

from wusa.docker import get_client
from wusa.docker import wusa_docker_run
from wusa.exceptions import DockerError
from wusa.exceptions import NoDockerServerFound


def test_get_client(monkeypatch):
    """Check that get_client uses 'from_env' interface to get DockerClient"""

    def mocked_from_env():
        return "success"

    # TODO: check if this can be done better
    #   - monkey patch requires to mock the function call inside 'wusa.docker'
    #   - better approach would be to mock 'docker.from_env' directly
    monkeypatch.setattr("wusa.docker.from_env", mocked_from_env)
    assert get_client() == "success"


def test_get_client_raises_NoClient(monkeypatch):
    """Check if get_client raises 'NoDockerServerFound' exception"""

    def raises_DockerException():
        raise DockerException

    monkeypatch.setattr("wusa.docker.from_env", raises_DockerException)

    with raises(NoDockerServerFound, match="failed to connect to docker"):
        get_client()


@fixture(name="patched_DockerClient")
def _mock_DockerClient(monkeypatch):
    class DockerContainers:
        @staticmethod
        def run(*arg, **kwargs):
            raise NotImplementedError

    class DockerClient:
        containers = DockerContainers()

    patched_client = DockerClient()

    def return_patched_client():
        return patched_client

    monkeypatch.setattr("wusa.docker.from_env", return_patched_client)
    yield patched_client


def test_wusa_docker_run_check_mocking(patched_DockerClient):
    class WhenCalled(Exception):
        pass

    def raise_when_called(*args, **kwargs):
        raise WhenCalled

    patched_DockerClient.containers.run = raise_when_called

    with raises(WhenCalled):
        wusa_docker_run("command")


def test_wusa_docker_run_check_args(patched_DockerClient):
    def check_args_and_kwargs(*args, **kwargs):
        assert args == ("wusarunner/base-linux:latest",)
        assert kwargs == {"command": "some command", "detach": True}

    patched_DockerClient.containers.run = check_args_and_kwargs
    wusa_docker_run("some command")


def test_wusa_docker_run_catches_APIError(patched_DockerClient):
    def raise_APIError(*args, **kwargs):
        raise APIError("")

    patched_DockerClient.containers.run = raise_APIError
    with raises(DockerError, match="error with docker occurred"):
        wusa_docker_run("")


def test_wusa_docker_run_catches_ImageNotFound(patched_DockerClient):
    def raise_ImageNotFound(*args, **kwargs):
        raise ImageNotFound("")

    patched_DockerClient.containers.run = raise_ImageNotFound
    with raises(DockerError, match="Image not found"):
        wusa_docker_run("")
