# -*- coding: utf-8 -*-
from collections import namedtuple
from urllib.parse import urlencode

import pytest
import requests

from wusa import WUSA_CLIENT_ID
from wusa.auth import gh_user_verification_codes


@pytest.fixture(name="mock_response")
def _response(monkeypatch):
    Response = namedtuple("Response", ["status_code", "text"])

    def _mocking(expected_url, expected_status_code, expected_data, query_key):
        def mocked_post(url, data):
            assert url == expected_url
            for expected_key, expected_val in expected_data.items():
                assert expected_key in data
                assert data[expected_key] == expected_val

            return Response(status_code=expected_status_code, text=query_key)

        monkeypatch.setattr(requests, "post", mocked_post)

    return _mocking


def test_gh_user_verification_codes_return_value(mock_response):
    expected_dict = {
        # chosen randomly
        "device_code": "abc123",
        "user_code": "BCDE-DCEF",
        "verification_uri": "https://some_uri",
        "expires_in": 1,
        "interval": 5,
    }
    mock_response(
        "https://github.com/login/device/code",
        200,
        {"client_id": WUSA_CLIENT_ID},
        urlencode(expected_dict),
    )

    resp = gh_user_verification_codes()

    assert isinstance(resp, dict)
    for expected_key, expected_value in expected_dict.items():
        assert expected_key in resp
        assert resp[expected_key] == expected_value
