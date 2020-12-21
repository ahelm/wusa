from pathlib import Path
import pytest
from wusa.utils import requires_config_file


@pytest.fixture(name="config_exist")
def _config_file_exist(monkeypatch):
    """Patches any Path.exists() call and returns True"""

    def always_true(*args, **kwargs):
        return True

    monkeypatch.setattr(Path, "exists", always_true)


@pytest.fixture(name="config_does_not_exist")
def _config_file_does_not_exist(monkeypatch):
    """Patches any Path.exists() call and returns False"""

    def always_false(*args, **kwargs):
        return False

    monkeypatch.setattr(Path, "exists", always_false)


def test_requires_config_file_exist(config_exist):
    """Checks if decorator `requires_config_file` decorates function properly."""

    @requires_config_file
    def dummy():
        return "something"

    assert dummy() == "something"


def test_requires_config_file_does_not_exist(config_does_not_exist, capsys):
    """Checks if `requires_config_file` prints to run `wusa init` and exists."""

    @requires_config_file
    def dummy():
        pass

    with pytest.raises(SystemExit):
        dummy()

    output = capsys.readouterr()
    assert "wusa init" in output.err
