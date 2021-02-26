# -*- coding: utf-8 -*-
import json
from string import ascii_lowercase

from pytest import fixture

from wusa.runners import Runner
from wusa.runners import RunnersList
from wusa.runners import open_runner_file


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
        "labels": ["label1", "label2", "some_other_label"],
    }
    assert runner.as_dict() == expected_dict


@fixture(name="mocked_wusa_base_dir")
def _mock_wusa_basedir(tmp_path, monkeypatch):
    new_basedir = tmp_path / "wusa-new-basedir"
    new_basedir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("wusa.runners.WUSA_BASE_DIR", new_basedir)
    yield new_basedir


@fixture(name="mocked_runners_json")
def _mock_runners_json(mocked_wusa_base_dir):
    runner_file = mocked_wusa_base_dir / "runners.json"
    runner_file.touch()
    yield runner_file


def test_open_runner_file(mocked_wusa_base_dir):
    runner_file = mocked_wusa_base_dir / "runners.json"

    with open_runner_file("w") as fp:
        fp.write("something")

    assert runner_file.exists()
    assert runner_file.read_text() == "something"


def test_RunnerList_no_runners(mocked_runners_json):
    mocked_runners_json.write_text(json.dumps([]))
    assert len(RunnersList()) == 0


def test_RunnerList_one_runner(mocked_runners_json):
    runner_dict = {
        "name": "somename",
        "repo": "some/repo",
        "labels": ["label1", "label2", "some_other_label"],
    }
    mocked_runners_json.write_text(json.dumps([Runner(**runner_dict).as_dict()]))
    assert len(RunnersList()) == 1
