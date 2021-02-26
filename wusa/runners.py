# -*- coding: utf-8 -*-
from contextlib import contextmanager
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from string import ascii_lowercase
from typing import IO
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
        d = asdict(self)
        d["url"] = self.url
        return d


class _RunnerList:
    def __init__(self) -> None:
        pass


RunnerList = _RunnerList()