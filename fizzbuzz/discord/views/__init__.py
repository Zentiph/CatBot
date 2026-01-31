"""A collection of ui Views used for the bot."""

__author__ = "Gavin Borne"
__license__ = "MIT"  # noqa: RUF067 (disables "no code in __init__", allowing for __license__ to be defined here)

__all__ = ["CarouselView", "RestrictedModal", "RestrictedView"]

from .carousel_view import CarouselView
from .restricted_view import RestrictedModal, RestrictedView
