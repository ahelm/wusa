# -*- coding: utf-8 -*-
from string import ascii_lowercase

from wusa.runners import Runner


def test_Runner_init():
    runner = Runner("somename", "some/repo", ["some_other_label", "label1", "label2"])

    assert runner.name == "somename"
    assert runner.repo == "some/repo"
    expected_labels = sorted(["label1", "label2", "some_other_label"])
    assert all(e == g for e, g in zip(expected_labels, runner.labels))
    assert runner.labels == ["label1", "label2", "some_other_label"]
    assert runner.url == "https://github.com/some/repo"


def test_Runner_new():
    runner = Runner.new("some/repo", ["some_label"])

    assert isinstance(runner, Runner)
    assert runner.name.startswith("wusa-")
    # without initial 'wusa-' (len == 5)
    assert all(c in ascii_lowercase for c in runner.name[5:])


def test_Runner_as_dict():
    runner = Runner("somename", "some/repo", ["some_other_label", "label1", "label2"])
    expected_dict = {
        "name": "somename",
        "repo": "some/repo",
        "url": "https://github.com/some/repo",
        "labels": ["label1", "label2", "some_other_label"],
    }
    assert runner.as_dict() == expected_dict
