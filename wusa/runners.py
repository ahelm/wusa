# -*- coding: utf-8 -*-
from contextlib import contextmanager
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from json import dumps
from json import loads
from string import ascii_lowercase
from typing import IO
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Union

from shortuuid import ShortUUID

from . import WUSA_BASE_DIR

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
    def _runner_list(self) -> List[Runner]:
        with open_runner_file(mode="r") as fp:
            raw_list = loads(fp.read())

        runner_list = []
        for entry in raw_list:
            runner_list.append(Runner(**entry))

        return runner_list

    @_runner_list.setter
    def _runner_list(self, list_runners: List[Runner]) -> None:
        processed_list = []
        for runner in list_runners:
            processed_list.append(runner.as_dict())

        with open_runner_file(mode="w") as fp:
            fp.write(dumps(processed_list))

    def __len__(self) -> int:
        return len(self._runner_list)

    def __getitem__(self, key: Any) -> Runner:
        return self._runner_list[key]

    def create_new_runner(self, repo: str, labels: List[str] = []) -> None:
        runners = self._runner_list
        new_runner = Runner.new(repo, labels)
        runners.append(new_runner)
        self._runner_list = runners


Runners = RunnersList()
