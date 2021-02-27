# -*- coding: utf-8 -*-
from typing import Optional
from typing import Protocol

from docker import from_env
from docker.client import DockerClient
from docker.errors import APIError
from docker.errors import DockerException
from docker.errors import ImageNotFound

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


def wusa_docker_run(
    command: str,
    image: str,
    name: str,
    logger: Optional[Logger] = None,
    substring_to_finish_logging: Optional[str] = None,
) -> DockerClient.containers:
    client = get_client()
    try:
        container = client.containers.run(
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
    container: DockerClient.containers,
    image_name: str,
    tag: str = "latest",
) -> None:
    try:
        container.commit(repository=image_name, tag=tag)
    except APIError:
        raise DockerError("Error during 'docker commit' encountered")


def wusa_docker_remove(
    container: DockerClient.containers,
) -> None:
    try:
        container.remove()
    except APIError:
        raise DockerError("Error during 'docker remove' encountered")
