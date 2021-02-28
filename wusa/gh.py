# -*- coding: utf-8 -*-
from asyncio import get_event_loop
from typing import Any
from typing import Dict
from typing import Union
from urllib.parse import parse_qs

from aiohttp import ClientSession
from gidgethub.aiohttp import GitHubAPI
from requests import post
from requests.exceptions import HTTPError

from . import WUSA_BASE_DIR
from .exceptions import GHError
from .exceptions import NoAccessToken
from .exceptions import PendingError

_location_access_token = WUSA_BASE_DIR / ".access_token"
_CLIENT_ID = "070dcc7e8ff3a7c087d5"


def obtain_token() -> str:
    if not _location_access_token.exists():
        raise NoAccessToken
    return _location_access_token.read_text()


def save_access_token(token: str) -> None:
    _location_access_token.write_text(token)


async def async_get_gh_api(api: str, token: str):
    async with ClientSession() as session:
        gh = GitHubAPI(session, "wusa", oauth_token=token)
        return await gh.getitem(api)


async def async_post_gh_api(api: str, token: str, data: Dict[str, Any]):
    async with ClientSession() as session:
        gh = GitHubAPI(session, "wusa", oauth_token=token)
        return await gh.post(api, data=data)


def get_gh_api(api: str) -> Dict[str, Any]:
    token = obtain_token()
    loop = get_event_loop()
    return loop.run_until_complete(async_get_gh_api(api, token))


def post_gh_api(api: str, data: Dict[str, Any] = {}) -> Dict[str, Any]:
    token = obtain_token()
    loop = get_event_loop()
    return loop.run_until_complete(async_post_gh_api(api, token, data))


def get_gh_verification_codes() -> Dict[str, Union[str, int]]:
    url = "https://github.com/login/device/code"
    data = {"client_id": _CLIENT_ID, "scope": "repo"}

    try:
        response = post(url, data=data)
        response.raise_for_status()
    except HTTPError:
        raise GHError("Received an non-ok status code")

    # Unpack response parameters
    # https://docs.github.com/en/developers/apps/authorizing-oauth-apps#response-parameters
    response_data: Dict[str, Union[str, int]] = {
        k: v.pop() for k, v in parse_qs(response.text).items()
    }
    response_data["expires_in"] = int(response_data["expires_in"])
    response_data["interval"] = int(response_data["interval"])

    return response_data


def get_gh_access_token(device_code: str) -> str:
    url = "https://github.com/login/oauth/access_token"
    data = {
        "client_id": _CLIENT_ID,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }

    try:
        response = post(url, data=data)
        response.raise_for_status()
    except HTTPError:
        raise GHError("Received an non-ok status code")

    response_data = {k: v.pop() for k, v in parse_qs(response.text).items()}

    # if error in response -> requires to wait
    if "error" in response_data:
        raise PendingError

    return response_data["access_token"]
