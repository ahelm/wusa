# -*- coding: utf-8 -*-
import json
from string import ascii_lowercase

from pytest import fixture

from wusa.runners import Runner
from wusa.runners import Runners
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
    runner_file.write_text(json.dumps([]))
    yield runner_file


def test_open_runner_file(mocked_wusa_base_dir):
    runner_file = mocked_wusa_base_dir / "runners.json"

    with open_runner_file("w") as fp:
        fp.write("something")

    assert runner_file.exists()
    assert runner_file.read_text() == "something"


def test_RunnerList_no_runners(mocked_runners_json):
    assert len(Runners) == 0


def test_RunnerList_one_runner(mocked_runners_json):
    runner_dict = {
        "name": "somename",
        "repo": "some/repo",
        "labels": ["label1", "label2", "some_other_label"],
    }
    mocked_runners_json.write_text(json.dumps([Runner(**runner_dict).as_dict()]))
    assert len(Runners) == 1


def test_RunnerList_new(mocked_runners_json, monkeypatch):
    def do_nothing_and_return_None(*args, **kwargs):
        return None

    monkeypatch.setattr("wusa.runners.wusa_docker_run", do_nothing_and_return_None)
    monkeypatch.setattr("wusa.runners.wusa_docker_remove", do_nothing_and_return_None)
    monkeypatch.setattr("wusa.runners.wusa_docker_commit", do_nothing_and_return_None)

    assert len(Runners) == 0
    Runners.create_new_runner("some/repo", "abcdef-token", ["some_label", "some-more"])
    assert len(Runners) == 1
    assert Runners[-1].name.startswith("wusa-")
    assert Runners[-1].repo == "some/repo"


def test_RunnerList_new_check_run_call_args(mocked_runners_json, monkeypatch):
    def do_nothing_and_return_None(*args, **kwargs):
        return None

    def check_args(command, image, name):
        # keep space for checking for surrounded space
        assert " --unattended " in command
        assert " --url https://github.com/some/repo " in command
        assert " --name wusa-" in command
        assert " --replace " in command
        assert " --token abcdeftoken " in command
        assert image == "wusarunner/base-linux:latest"
        assert name.startswith("wusa-")

    monkeypatch.setattr("wusa.runners.wusa_docker_run", check_args)
    monkeypatch.setattr("wusa.runners.wusa_docker_remove", do_nothing_and_return_None)
    monkeypatch.setattr("wusa.runners.wusa_docker_commit", do_nothing_and_return_None)

    Runners.create_new_runner("some/repo", "abcdeftoken", ["some_label", "some-more"])


def test_RunnerList_iteration(monkeypatch):
    # patch internal representation of runners and replace by list of str
    monkeypatch.setattr(RunnersList, "_runners", ["a", "b", "c"])

    assert tuple(RunnersList()) == ("a", "b", "c")
    expected_value = ["a", "b", "c"]
    assert len(expected_value) == len(RunnersList())
    for i, content in enumerate(RunnersList()):
        assert content == expected_value[i]
