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
    image: str = "wusarunner/base-linux:latest",
    logger: Optional[Logger] = None,
) -> None:
    client = get_client()
    try:
        container = client.containers.run(image, command=command, detach=True)
        if logger:
            for line in container.logs(stream=True):
                if decoded_cleaned_line := line.decode("utf-8").strip():
                    logger.log(decoded_cleaned_line)
        else:
            container.wait()

    # ATTENTION: ImageNotFound requires to be raised before APIError
    #            inheritance order (ImageNotFound <- NotFound <- APIError)
    except ImageNotFound:
        raise DockerError(f"Image '{image}' not found")
    except APIError:
        raise DockerError("During run an error with docker occurred")
