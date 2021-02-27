# -*- coding: utf-8 -*-
from typing import Optional
from typing import Protocol

from docker import from_env
from docker.client import DockerClient
from docker.errors import APIError
from docker.errors import DockerException
from docker.errors import ImageNotFound
from docker.errors import NotFound
from docker.models.containers import Container

from .exceptions import DockerError
from .exceptions import NoDockerServerFound


class Logger(Protocol):
    def log(self, *args, **kwargs) -> None:
        ...


def get_client() -> DockerClient:
    try:
        return from_env()
    except DockerException:
        raise NoDockerServerFound("Wusa failed to connect to docker server")


def wusa_docker_get(name: str) -> Container:
    client = get_client()
    try:
        container: Container = client.containers.get(name)
        if "org.wusa.container-name" in container.labels:
            return container
        else:
            raise DockerError(f"No valid wusa container '{name}' found")
    except NotFound:
        raise DockerError(f"Did not find container '{name}'")
    except APIError:
        raise DockerError("Error encountered while trying to get container")


def wusa_docker_run(
    command: str,
    image: str,
    name: str,
    logger: Optional[Logger] = None,
    substring_to_finish_logging: Optional[str] = None,
) -> Container:
    client = get_client()
    try:
        container: Container = client.containers.run(
            image,
            command=command,
            detach=True,
            labels={"org.wusa.container-name": name},
        )

        if not logger:
            return container

        for line in container.logs(stream=True):
            decoded_cleaned_line = line.decode("utf-8").strip()
            if decoded_cleaned_line:
                logger.log(decoded_cleaned_line)

            if decoded_cleaned_line == substring_to_finish_logging:
                break

        return container

    # ATTENTION: ImageNotFound requires to be raised before APIError
    #            inheritance order (ImageNotFound <- NotFound <- APIError)
    except ImageNotFound:
        raise DockerError(f"Image '{image}' not found")
    except APIError:
        raise DockerError("Error during 'docker run' encountered")


def wusa_docker_commit(
    container: Container,
    image_name: str,
    tag: str = "latest",
) -> None:
    try:
        container.commit(repository=image_name, tag=tag)
    except APIError:
        raise DockerError("Error during 'docker commit' encountered")


def wusa_docker_remove(
    container: Container,
) -> None:
    try:
        container.remove()
    except APIError:
        raise DockerError("Error during 'docker remove' encountered")
