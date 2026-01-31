"""HTTP helpers for requesting text or image data."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
import os
import time
from typing import Any
from urllib.parse import urlparse

import requests

from ..discord.info import VERSION

__author__ = "Gavin Borne"
__license__ = "MIT"

_DEFAULT_USER_AGENT = os.getenv(
    "HTTP_USER_AGENT",
    # clip leading 'v' from version
    f"FizzBuzz/{VERSION[1:]} (contact: zentiphdev@gmail.com)",
)

_DEFAULT_HEADERS = {"User-Agent": _DEFAULT_USER_AGENT}

_PER_HOST_MIN_INTERVAL_SECONDS = float(os.getenv("HTTP_PER_HOST_MIN_INTERVAL", "0.1"))

STATUS_OK = 200
"""The status code for an OK response."""


_last_request_time_by_host: dict[str, float] = {}


class ApiError(RuntimeError):
    """Raised when an API call fails in a user-facing manner."""


@dataclass(frozen=True)
class ApiJsonResponse:
    """JSON response data from an API call."""

    status_code: int
    """The status code of the response."""
    json: Any
    """The JSON payload of the response."""
    url: str
    """The original URL that the request was sent to."""


def _merge_headers_with_defaults(
    headers: Mapping[str, str] | None, /
) -> dict[str, str]:
    merged = dict(_DEFAULT_HEADERS)
    if headers:
        merged.update(headers)
    return merged


def _get_host_from_url(url: str, /) -> str:
    try:
        return urlparse(url).netloc.lower()
    except (TypeError, AttributeError):
        return ""


def _throttle_host(url: str, /) -> None:  # best-effort per-host throttle
    if _PER_HOST_MIN_INTERVAL_SECONDS <= 0:
        return

    host = _get_host_from_url(url)
    if not host:
        return

    now = time.monotonic()
    last = _last_request_time_by_host.get(host, 0.0)
    wait = _PER_HOST_MIN_INTERVAL_SECONDS - (now - last)
    if wait > 0:
        time.sleep(wait)
    _last_request_time_by_host[host] = time.monotonic()


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
        _throttle_host(url)
        merged_headers = _merge_headers_with_defaults(headers)

        response = requests.get(
            url, headers=merged_headers, params=params, timeout=timeout
        )
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
        _throttle_host(url)
        merged_headers = _merge_headers_with_defaults(headers)

        response = requests.get(url, headers=merged_headers, timeout=timeout)
        if response.status_code != STATUS_OK:
            raise ApiError(
                f"Failed to fetch bytes from {url} (status {response.status_code})"
            )
        return response.content

    return await asyncio.to_thread(do)
