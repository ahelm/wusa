# -*- coding: utf-8 -*-
from typing import Dict
from typing import Union
from urllib.parse import parse_qs

import requests

from wusa import WUSA_CLIENT_ID
from wusa.utils import is_valid_status_code


def gh_user_verification_codes() -> Dict[str, Union[str, int]]:
    response = requests.post(
        "https://github.com/login/device/code",
        data={
            "client_id": WUSA_CLIENT_ID,
        },
    )

    if not is_valid_status_code(
        response.status_code,
        "Can not obtain user verification codes from GitHub.",
    ):
        raise ConnectionError

    # https://docs.github.com/en/developers/apps/authorizing-oauth-apps#response-parameters
    response_data: Dict[str, Union[str, int]] = {
        k: v.pop() for k, v in parse_qs(response.text).items()
    }
    response_data["expires_in"] = int(response_data["expires_in"])
    response_data["interval"] = int(response_data["interval"])

    return response_data
