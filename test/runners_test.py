# -*- coding: utf-8 -*-
from wusa.runners import Runner


def test_Runner_init():
    runner = Runner("somename", "some/repo", ["some_other_label", "label1", "label2"])

    assert runner.name == "somename"
    assert runner.repo == "some/repo"
    expected_labels = sorted(["label1", "label2", "some_other_label"])
    assert all(e == g for e, g in zip(expected_labels, runner.labels))
    assert runner.labels == ["label1", "label2", "some_other_label"]
    assert runner.url == "https://github.com/some/repo"
