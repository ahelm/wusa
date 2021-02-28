# -*- coding: utf-8 -*-
from contextlib import contextmanager
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from json import dumps
from json import loads
from string import ascii_lowercase
from typing import IO
from typing import Dict
from typing import Generator
from typing import List
from typing import Union

from shortuuid import ShortUUID

from . import WUSA_BASE_DIR
from .docker import wusa_docker_commit
from .docker import wusa_docker_remove
from .docker import wusa_docker_run

UUID = ShortUUID(alphabet=ascii_lowercase)


@contextmanager
def open_runner_file(mode: str) -> Generator[IO, None, None]:
    runner_file = WUSA_BASE_DIR / "runners.json"
    runner_file.touch()
    with runner_file.open(mode) as fp:
        yield fp


@dataclass
class Runner:
    name: str
    repo: str
    labels: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.labels = sorted(self.labels)

    @classmethod
    def new(cls, repo: str, labels: List[str] = []) -> "Runner":
        name = "wusa-" + UUID.random(length=8)
        return cls(name, repo, labels)

    @property
    def url(self) -> str:
        return f"https://github.com/{self.repo}"

    def as_dict(self) -> Dict[str, Union[str, List[str]]]:
        return asdict(self)


class RunnersList:
    @property
    def _runners(self) -> List[Runner]:
        with open_runner_file(mode="r") as fp:
            raw_list = loads(fp.read())

        runner_list = []
        for entry in raw_list:
            runner_list.append(Runner(**entry))

        return runner_list

    @_runners.setter
    def _runners(self, list_runners: List[Runner]) -> None:
        processed_list = []
        for runner in list_runners:
            processed_list.append(runner.as_dict())

        with open_runner_file(mode="w") as fp:
            fp.write(dumps(processed_list))

    def __len__(self) -> int:
        return len(self._runners)

    def __getitem__(self, key: int) -> Runner:
        return self._runners[key]

    def create_new_runner(self, repo: str, token: str, labels: List[str] = []) -> None:
        runners = self._runners
        new_runner = Runner.new(repo, labels)
        cmd = (
            f"./config.sh "
            f" --unattended"
            f" --url {new_runner.url}"
            f" --name {new_runner.name}"
            f" --replace"
            f" --token {token}"
        )
        container = wusa_docker_run(
            f"bash -c '{cmd}'", "wusarunner/base-linux:latest", new_runner.name
        )
        wusa_docker_commit(container, new_runner.name)
        wusa_docker_remove(container)
        runners.append(new_runner)
        self._runners = runners


Runners = RunnersList()
