# -*- coding: utf-8 -*-
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import List
from typing import Union


@dataclass
class Runner:
    name: str
    repo: str
    labels: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.labels = sorted(self.labels)

    @property
    def url(self) -> str:
        return f"https://github.com/{self.repo}"

    def as_dict(self) -> Dict[str, Union[str, List[str]]]:
        d = asdict(self)
        d["url"] = self.url
        return d


class RunnerList:
    pass
