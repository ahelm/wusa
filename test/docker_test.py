# -*- coding: utf-8 -*-
from docker.errors import APIError
from docker.errors import DockerException
from docker.errors import ImageNotFound
from pytest import fixture
from pytest import raises

from wusa.docker import get_client
from wusa.docker import wusa_docker_commit
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
    class DockerContainer:
        @staticmethod
        def run(*arg, **kwargs):
            raise NotImplementedError

        @staticmethod
        def wait(*args, **kwargs):
            raise NotImplementedError

        @staticmethod
        def logs(*args, **kwargs):
            raise NotImplementedError

    class DockerClient:
        containers = DockerContainer()

    patched_client = DockerClient()

    def return_patched_client():
        return patched_client

    def return_container_of_patched_client(*args, **kwargs):
        return patched_client.containers

    monkeypatch.setattr("wusa.docker.from_env", return_patched_client)
    patched_client.containers.run = return_container_of_patched_client
    yield patched_client


class HasBeenCalled(Exception):
    pass


def test_wusa_docker_run_check_mocking(patched_DockerClient):
    def raise_when_called(*args, **kwargs):
        raise HasBeenCalled

    patched_DockerClient.containers.run = raise_when_called

    with raises(HasBeenCalled):
        wusa_docker_run("command", "some_image")


def test_wusa_docker_run_calls_docker_run(patched_DockerClient):
    def check_args_and_kwargs(*args, **kwargs):
        assert args == ("some_image",)
        assert kwargs == {"command": "some command", "detach": True}
        return patched_DockerClient.containers  # run should return DockerContainer

    patched_DockerClient.containers.run = check_args_and_kwargs

    wusa_docker_run("some command", "some_image")


def test_wusa_docker_run_catches_APIError(patched_DockerClient):
    def raise_APIError(*args, **kwargs):
        raise APIError(message="")

    patched_DockerClient.containers.run = raise_APIError
    with raises(DockerError, match="Error during run encountered"):
        wusa_docker_run("", "some_image")


def test_wusa_docker_run_catches_ImageNotFound(patched_DockerClient):
    def raise_ImageNotFound(*args, **kwargs):
        raise ImageNotFound(message="")

    patched_DockerClient.containers.run = raise_ImageNotFound
    with raises(DockerError, match="Image 'some_image' not found"):
        wusa_docker_run("", image="some_image")


def test_wusa_docker_run_calls_container_logs(patched_DockerClient):
    messages = [b"some byte string with newline\n"]
    clean_messages = [s.decode("utf-8").strip() for s in messages]

    def docker_logs(**kwargs):
        assert "stream" in kwargs
        assert kwargs["stream"]
        for message in messages:
            yield message
        raise HasBeenCalled

    class Logger:
        def log(self, message):
            if message not in clean_messages:
                raise NotImplementedError

    patched_DockerClient.containers.logs = docker_logs

    with raises(HasBeenCalled):
        wusa_docker_run("somme_command", "some_image", logger=Logger())


def test_wusa_docker_commit():
    class DummyContainer:
        @staticmethod
        def commit(repository=None, tag=None):
            assert repository == "new_image_name"
            assert tag == "new_tag"
            raise HasBeenCalled

    with raises(HasBeenCalled):
        wusa_docker_commit(DummyContainer(), "new_image_name", "new_tag")


def test_wusa_docker_commit_raises_DockerError():
    class DummyContainer:
        @staticmethod
        def commit(repository=None, tag=None):
            raise APIError(message="")

    with raises(DockerError, match="Error during commit encountered"):
        wusa_docker_commit(DummyContainer(), "new_image_name")
