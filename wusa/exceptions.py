# -*- coding: utf-8 -*-
from gidgethub import BadRequest  # noqa: F401


class NoDockerServerFound(Exception):
    pass


class DockerError(Exception):
    pass


class RunnerFileIOError(Exception):
    pass


class PendingError(Exception):
    pass
