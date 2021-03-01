# -*- coding: utf-8 -*-
from asyncio import get_event_loop
from typing import Any
from typing import Dict
from typing import Optional
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
    """Get access token from ``WUSA_BASE_DIR/.access_token``

    Returns
    -------
        String as a token to access GitHub API.

    Raises
    ------
    ``NoAcccessToken``
        If file associated which hold access token does not exist.
    """
    if not _location_access_token.exists():
        raise NoAccessToken
    return _location_access_token.read_text()


def save_access_token(token: str) -> None:
    """Stores access token in ``WUSA_BASE_DIR/.access_token``

    Parameter
    ---------
    token
        Token which will be written in file.
    """
    _location_access_token.write_text(token)


async def async_get_gh_api(
    api: str,
    token: str,
) -> Dict[str, Any]:
    """Coroutine which sends a GET request to GitHub API.

    Parameters
    ----------
    api
        API endpoint to which a GET requests is send.

    token
        Auth token for GitHub to access API endpoint.

    Returns
    -------
        Dictionary containing respond to request.
    """
    async with ClientSession() as session:
        gh_api = GitHubAPI(session, "wusa", oauth_token=token)
        return await gh_api.getitem(api)


async def async_post_gh_api(
    api: str,
    token: str,
    data: Dict[str, Union[str, int]],
) -> Dict[str, Any]:
    """Coroutine which sends a POST request to GitHub API.

    Parameters
    ----------
    api
        API endpoint to which a POST requests is send.

    token
        Auth token for GitHub to access API endpoint.

    data
        Dictionary with additional data to attach to POST request

    Returns
    -------
        Dictionary containing respond to request.
    """
    async with ClientSession() as session:
        gh_api = GitHubAPI(session, "wusa", oauth_token=token)
        return await gh_api.post(api, data=data)


def get_gh_api(api: str) -> Dict[str, Any]:
    """Wrapper function for GET requests to call GitHub API in async mode.

    Parameters
    ----------
    api
        API endpoint to which a GET requests is send.

    Returns
    -------
        Dictionary containing respond to request.
    """
    token = obtain_token()
    loop = get_event_loop()
    return loop.run_until_complete(async_get_gh_api(api, token))


def post_gh_api(
    api: str,
    data: Optional[Dict[str, Union[str, int]]] = None,
) -> Dict[str, Any]:
    """Wrapper function for POST requests to call GitHub API in async mode.

    Parameters
    ----------
    api
        API endpoint to which a POST requests is send.

    data
        Dictionary with additional data to attach to POST request

    Returns
    -------
        Dictionary containing respond to request.
    """
    token = obtain_token()
    loop = get_event_loop()
    data_to_send = data or {}
    return loop.run_until_complete(async_post_gh_api(api, token, data_to_send))


def api_runner_registration(repo: str) -> str:
    """Helper function which returns the API endpoint for runner registration.

    Parameter
    ---------
    repo
        Repository in the format "some_user/repo_name".

    Returns
    -------
        String containing the full API endpoint to obtain registration token.
    """
    return f"/repos/{repo}/actions/runners/registration-token"


def api_runner_removal(repo: str) -> str:
    """Helper function which returns the API endpoint for runner removal.

    Parameter
    ---------
    repo
        Repository in the format "some_user/repo_name".

    Returns
    -------
        String containing the full API endpoint to obtain token for runner removal.
    """
    return f"/repos/{repo}/actions/runners/remove-token"


def api_runner_list(repo: str) -> str:
    """Helper function which returns the API endpoint to list all runners.

    Parameter
    ---------
    repo
        Repository in the format "some_user/repo_name".

    Returns
    -------
        String containing the full API endpoint to obtain token for runner list.
    """
    return f"/repos/{repo}/actions/runners"


def get_gh_verification_codes() -> Dict[str, Union[str, int]]:
    """Function which gets device codes

    Returns
    -------
        Dictionary containing the response of the
    """
    url = "https://github.com/login/device/code"
    data = {"client_id": _CLIENT_ID, "scope": "repo"}

    try:
        response = post(url, data=data)
        response.raise_for_status()
    except HTTPError as exc:
        raise GHError("Received an non-ok status code") from exc

    # Unpack response parameters
    # https://docs.github.com/en/developers/apps/authorizing-oauth-apps#response-parameters
    response_data: Dict[str, Union[str, int]] = {
        k: v.pop() for k, v in parse_qs(response.text).items()
    }
    response_data["expires_in"] = int(response_data["expires_in"])
    response_data["interval"] = int(response_data["interval"])

    return response_data


def get_gh_access_token(device_code: str) -> str:
    """Gets access code for a given device code.

    Parameter
    ---------
    device_code
        Pre-generated device code.

    Returns
    -------
        Dictionary containing the response of the
    """
    url = "https://github.com/login/oauth/access_token"
    data = {
        "client_id": _CLIENT_ID,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }

    try:
        response = post(url, data=data)
        response.raise_for_status()
    except HTTPError as exc:
        raise GHError("Received an non-ok status code") from exc

    response_data = {k: v.pop() for k, v in parse_qs(response.text).items()}

    # if error in response -> requires to wait
    if "error" in response_data:
        raise PendingError

    return response_data["access_token"]
