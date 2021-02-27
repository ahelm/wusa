# -*- coding: utf-8 -*-
from docker import from_env
from docker.client import DockerClient
from docker.errors import DockerException

from .exceptions import NoDockerServerFound


def get_client() -> DockerClient:
    try:
        return from_env()
    except DockerException:
        raise NoDockerServerFound("Wusa failed to connect to docker server")
