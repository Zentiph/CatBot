"""HTTP helpers for requesting text or image data."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import requests

__author__ = "Gavin Borne"
__license__ = "MIT"

_STATUS_OK = 200


class ApiError(RuntimeError):
    """Raised when an API call fails in a user-facing manner."""


@dataclass(frozen=True)
class ApiJsonResponse:
    """JSON response data from an API call."""

    status_code: int
    json: Any
    url: str


async def http_get_json(
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, Any] | None = None,
    timeout: float = 10.0,
) -> ApiJsonResponse:
    """GET JSON using requests, offloaded to a worker thread.

    Args:
        url (str): The URL to send the request to.
        headers (Mapping[str, str] | None, optional): Optional headers to include.
            Defaults to None.
        params (Mapping[str, Any] | None, optional): Optional parameters to include.
            Defaults to None.
        timeout (float, optional): The max time to wait for a response.
            Defaults to 10.0.

    Returns:
        ApiJsonResponse: The response data.
    """

    def do() -> ApiJsonResponse:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        try:
            payload = response.json() if response.content else None
        except Exception as e:
            raise ApiError(
                f"Invalid JSON from {url} (status {response.status_code})"
            ) from e
        return ApiJsonResponse(status_code=response.status_code, json=payload, url=url)

    return await asyncio.to_thread(do)


async def http_get_bytes(
    url: str, *, headers: Mapping[str, str] | None = None, timeout: float = 10.0
) -> bytes:
    """GET raw bytes (mainly for images) using requests, offloaded to a worker thread.

    Args:
        url (str): The URL to send the request to.
        headers (Mapping[str, str] | None, optional): Optional headers to include.
            Defaults to None.
        timeout (float, optional): The max time to wait for a response.
            Defaults to 10.0.

    Returns:
        bytes: The raw bytes received.
    """

    def do() -> bytes:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code != _STATUS_OK:
            raise ApiError(
                f"Failed to fetch bytes from {url} (status {response.status_code})"
            )
        return response.content

    return await asyncio.to_thread(do)
