from ctypes import ArgumentError
from typing import Optional
from pathlib import Path
from os import chdir
import json

from click.core import Option
from wusa.utils import requires_config_file
from click.testing import CliRunner, Result
import pytest
import keyring

from wusa.cli import main
from wusa.cli import init
import wusa


@pytest.fixture(name="cwd")
def _changed_cwd(tmp_path):
    """Changes current working directory to temporary directory"""
    current_path = Path.cwd()

    chdir(tmp_path)
    yield tmp_path

    chdir(current_path)


@pytest.fixture(name="patched_keyring")
def _patch_keyring(monkeypatch):
    """Monkeypatches keyring functionality"""

    class PatchedKeyring:
        service_name: Optional[str] = None
        username: Optional[str] = None
        password: Optional[str] = None

        def set_password(self, service_name: str, username: str, password: str):
            self.service_name = service_name
            self.username = username
            self.password = password

        def get_password(self, service_name: str, username: str):
            if service_name == self.service_name and username == self.username:
                return self.password
            else:
                return None

        def delete_password(self, service_name: str, username: str):
            raise NotImplementedError

    patched_keyring = PatchedKeyring()

    monkeypatch.setattr(keyring, "set_password", patched_keyring.set_password)
    monkeypatch.setattr(keyring, "get_password", patched_keyring.get_password)
    monkeypatch.setattr(keyring, "delete_password", patched_keyring.delete_password)

    yield patched_keyring


@pytest.fixture(name="tmp_configdir")
def _custom_configfile(tmp_path):
    """Changes wusa's config dir and config file to a test specific dir/file"""
    prev_config_dir = wusa.WUSA_CONFIG_DIR
    prev_config_file = wusa.WUSA_CONFIG_FILE

    wusa.WUSA_CONFIG_DIR = tmp_path / "dummy_config_dir"
    wusa.WUSA_CONFIG_FILE = tmp_path / "dummy_config_dir" / "config.json"

    yield

    wusa.WUSA_CONFIG_DIR = prev_config_dir
    wusa.WUSA_CONFIG_FILE = prev_config_file


def test_main():
    """Default behavior for `wusa` - prints help message"""
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert result.output == runner.invoke(main, ["--help"]).output


def test_new_no_config(config_does_not_exist):
    """Invoking new if no valid config exists should result in error"""
    runner = CliRunner()
    result = runner.invoke(main, ["new"])
    assert result.exit_code == 2


def test_init_noargs():
    """Init should fail if no args are provided"""
    runner = CliRunner()
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 2


def test_init_help():
    """Init help should be available"""
    runner = CliRunner()
    result = runner.invoke(main, ["init", "--help"])
    assert result.exit_code == 0


def test_init_correct_setting_of_keyring(cwd, patched_keyring):
    """Checks init uses correct keyring method"""
    runner = CliRunner()
    result = runner.invoke(main, ["init", "ABCD", "."])
    assert result.exit_code == 0
    assert patched_keyring.service_name == wusa.WUSA_SERVICE_NAME
    assert patched_keyring.username == wusa.WUSA_USERNAME
    assert patched_keyring.password == "ABCD"


def test_init_storing_of_config(cwd, tmp_configdir, patched_keyring):
    runner = CliRunner()
    result = runner.invoke(main, ["init", "ABCD", "."])

    assert result.exit_code == 0
    assert Path(wusa.WUSA_CONFIG_FILE).exists()


def test_init_fails_on_files(cwd):
    """Providing existing file for base directory should fail"""
    new_file = cwd / "newfile.txt"
    new_file.touch()
    runner = CliRunner()
    result = runner.invoke(main, ["init", "ABCD", "newfile.txt"])
    assert result.exit_code == 2


def test_init_fails_non_existing(cwd):
    """Providing a non-existing directory should fail"""
    runner = CliRunner()
    result = runner.invoke(main, ["init", "ABCD", "non-existing-dir"])
    assert result.exit_code == 2
