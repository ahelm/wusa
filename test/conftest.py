from pathlib import Path

import pytest


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
