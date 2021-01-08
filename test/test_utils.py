# -*- coding: utf-8 -*-
from wusa.utils import generate_container_name
from wusa.utils import is_valid_url


def test_is_valid_url():
    assert is_valid_url("abc") is False
    assert is_valid_url("https://github.com/ahelm/wusa") is True


def test_generate_container_name():
    assert generate_container_name().startswith("wusa_")
    assert len(generate_container_name()) == 5 + 8
