# -*- coding: utf-8 -*-
from typing import Dict
from typing import Union
from urllib.parse import parse_qs

import requests

from wusa import WUSA_CLIENT_ID
from wusa.exception import PendingError
from wusa.utils import is_valid_status_code


def gh_user_verification_codes() -> Dict[str, Union[str, int]]:
    response = requests.post(
        "https://github.com/login/device/code",
        data={
            "client_id": WUSA_CLIENT_ID,
            "scope": "repo",
        },
    )

    if not is_valid_status_code(
        response.status_code,
        "https://github.com/login/device/code",
    ):
        raise ConnectionError

    # https://docs.github.com/en/developers/apps/authorizing-oauth-apps#response-parameters
    response_data: Dict[str, Union[str, int]] = {
        k: v.pop() for k, v in parse_qs(response.text).items()
    }
    response_data["expires_in"] = int(response_data["expires_in"])
    response_data["interval"] = int(response_data["interval"])

    return response_data


def gh_get_user_access_token(device_code: str) -> str:
    response = requests.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": WUSA_CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        },
    )

    if not is_valid_status_code(
        response.status_code,
        "https://github.com/login/oauth/access_token",
    ):
        raise ConnectionError

    response_data = {k: v.pop() for k, v in parse_qs(response.text).items()}

    if "error" in response_data:
        raise PendingError
    else:
        return response_data["access_token"]
