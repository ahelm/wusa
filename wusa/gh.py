# -*- coding: utf-8 -*-
import asyncio
from typing import Any
from typing import Dict

import aiohttp
from gidgethub.aiohttp import GitHubAPI

from .utils import token_else_raise_and_exit


async def async_get_gh_api(api: str, token: str):
    async with aiohttp.ClientSession() as session:
        gh = GitHubAPI(session, "wusa", oauth_token=token)
        return await gh.getitem(api)


async def async_post_gh_api(api: str, token: str, data: Dict[str, Any]):
    async with aiohttp.ClientSession() as session:
        gh = GitHubAPI(session, "wusa", oauth_token=token)
        return await gh.post(api, data=data)


def get_gh_api(api: str) -> Dict[str, Any]:
    token = token_else_raise_and_exit()
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_get_gh_api(api, token))


def post_gh_api(api: str, data: Dict[str, Any] = {}) -> Dict[str, Any]:
    token = token_else_raise_and_exit()
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_post_gh_api(api, token, data))
