# -*- coding: utf-8 -*-
from dataclasses import dataclass
from dataclasses import field
from typing import List


@dataclass
class Runner:
    name: str
    repo: str
    labels: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.labels = sorted(self.labels)

    @property
    def url(self) -> str:
        return f"https://github.com/{self.repo}"


class RunnerList:
    pass
