"""Functionality for the wrapped event.

The event is similar to Spotify Wrapped, in which it compiles message data from
throughout the year which will then have statistics run on it to create a presentation
for the server.
"""

__author__ = "Gavin Borne"
__license__ = "MIT"  # noqa: RUF067 (disables "no code in __init__", allowing for __license__ to be defined here)

__all__ = ["metric_store"]

from .metrics_store import metric_store
