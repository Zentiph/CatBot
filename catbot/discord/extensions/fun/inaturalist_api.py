"""Tools for interacting with the iNaturalist API for the /animal command."""

from dataclasses import dataclass
import html
import re
import secrets
from typing import Any

import discord
from discord import app_commands

from ....util.http import STATUS_OK, ApiError, http_get_json

__author__ = "Gavin Borne"
__license__ = "MIT"

INAT_TAXA_URL = "https://api.inaturalist.org/v1/taxa"
"""The URL for the iNaturalist taxa API."""

INAT_OBSERVATIONS_URL = "https://api.inaturalist.org/v1/observations"
"""The URL for the iNaturalist observations API."""

INAT_TAXA_AUTOCOMPLETE_URL = "https://api.inaturalist.org/v1/taxa/autocomplete"
"""The URL for the iNaturalist autocomplete API."""

AUTOCOMPLETE_MAX_OPTIONS = 10
"""The maximum number of iNaturalist autocomplete options to fetch."""

AUTOCOMPLETE_LABEL_MAX = 100
"""The maximum amount of characters that can be shown
per option in the autocomplete menu.
"""

AUTOCOMPLETE_CACHE_MAX = 128
"""The maximum size of the autocomplete cache for /animal."""

AUTOCOMPLETE_START_COUNT = 2
"""The number of characters that must be typed before autocomplete activates."""

INAT_OBSERVATIONS_IMAGE_FETCH_COUNT = 60
"""The number of images to fetch from iNaturalist observations."""

OBSERVATION_IMAGE_FETCH_ATTEMPTS = 15
"""The number of attempts to try when fetching images from iNaturalist observations."""

BAD_WORDS = re.compile(
    r"\b("
    r"skull|skeleton|bones|bone|dead|deceased|roadkill|carcass|corpse|remains|"
    r"taxidermy|pelt|hide|fur|skin|mount|mounted|trophy|"
    r"scat|poop|feces|dropping|tracks|track|footprint|pawprint|"
    r"specimen|museum|collection|preserved|"
    r"blood|bleeding|injury|injured|"
    r"genitals|testicles|penis|scrotum"
    r")\b",
    re.IGNORECASE,
)
"""A list of words that should be avoided when searching for iNaturalist photos."""

HTML_TAG_RE = re.compile(r"<[^>]+>")
"""Regex for an html tag."""

autocomplete_cache: dict[str, list[app_commands.Choice[str]]] = {}


@dataclass(frozen=True)
class AnimalResult:
    """The result of an animal search."""

    kind: str
    """The kind of animal."""
    image_url: str
    """The URL to the image found."""
    fact: str | None = None
    """A fact blurb about the animal."""
    source: str | None = None
    """The source of the animal and fact."""


def get_first_non_whitespace_str(*values: object) -> str | None:
    """Get the first non-whitespace only string in a group of objects.

    Returns:
        str | None: The first non-whitespace string, or None if there are none.
    """
    for v in values:
        if isinstance(v, str) and v.strip():
            return v
    return None


def normalize_animal_query(q: str) -> str:
    """Normalize an iNaturalist animal query by removing excess whitespace.

    Args:
        q (str): The query to normalize.

    Returns:
        str: The normalized query.
    """
    return " ".join(q.strip().split())


def clean_wiki_summary(text: str) -> str:
    """Clean the wiki summary of an animal of HTML tags.

    Args:
        text (str): The raw text.

    Returns:
        str: The cleaned result.
    """
    # turn &amp; etc. into real characters
    text = html.unescape(text)
    # remove tags like <b>, <i>, <br>, ...
    text = HTML_TAG_RE.sub("", text)
    # normalize whitespace a bit
    return " ".join(text.split()).strip()


def extract_inat_photo_url(photo_obj: object, /) -> str | None:
    """Extract an iNaturalist photo URL from the photo object.

    Args:
        photo_obj (object): The photo object given by iNaturalist.

    Returns:
        str | None: The photo URL, or None if it couldn't be found.
    """
    # iNat photos usually look like:
    # {"url": "https://static.inaturalist.org/photos/.../square.jpg?...",
    #  "attribution": "..."}
    if not isinstance(photo_obj, dict):
        return None
    return get_first_non_whitespace_str(
        photo_obj.get("url"), photo_obj.get("original_url"), photo_obj.get("large_url")
    )


def bump_inat_size(url: str, /) -> str:
    """Attempt to bump the size of an iNaturalist photo.

    Return the URL as is if it can't be improved.

    Args:
        url (str): The original image URL.

    Returns:
        str: The bumped image URL.
    """
    # iNat usually returns .../square.jpg, but can be bumped to bigger sizes.
    return (
        url.replace("/square.", "/large.")
        .replace("/square.jpg", "/large.jpg")
        .replace("/square.jpeg", "/large.jpeg")
        .replace("/square.png", "/large.png")
    )


def observation_seems_gross(obs: dict[str, Any]) -> bool:
    """Check if an observation is associated with the banned words list.

    Args:
        obs (dict[str, Any]): The observation payload.

    Returns:
        bool: Whether the observation should be skipped to be safe.
    """
    # fields that sometimes carry context
    text_fields = [
        obs.get("species_guess"),
        obs.get("description"),
    ]

    # tags are often useful
    tags = obs.get("tags")
    if isinstance(tags, list):
        text_fields.extend([t for t in tags if isinstance(t, str)])

    haystack = " ".join([t for t in text_fields if isinstance(t, str)])
    return bool(BAD_WORDS.search(haystack))


async def get_autocomplete_data(query: str, /) -> tuple[str, dict[str, Any]] | None:
    """Get the autocomplete data of an iNaturalist query.

    Args:
        query (str): The query.

    Returns:
        tuple[str, dict[str, Any]] | None: The autocomplete data,
            or None if nothing matched.
    """
    autocomplete_response = await http_get_json(
        INAT_TAXA_AUTOCOMPLETE_URL,
        params={"q": query, "per_page": AUTOCOMPLETE_MAX_OPTIONS},
        timeout=8,
    )

    if autocomplete_response.status_code != STATUS_OK:
        return None

    autocomplete_payload = autocomplete_response.json
    autocomplete_results = (
        autocomplete_payload.get("results")
        if isinstance(autocomplete_payload, dict)
        else None
    )

    if not isinstance(autocomplete_results, list) or not autocomplete_results:
        return None

    top = autocomplete_results[0]
    if not isinstance(top, dict):
        return None

    taxon_id = top.get("id")
    sci_name = get_first_non_whitespace_str(top.get("name"))

    # prefer fetching full taxon by id for consistent fields
    if isinstance(taxon_id, int):
        by_id = await http_get_json(f"{INAT_TAXA_URL}/{taxon_id}", timeout=10)
        if by_id.status_code == STATUS_OK:
            by_id_json = by_id.json
            by_id_results = (
                by_id_json.get("results") if isinstance(by_id_json, dict) else None
            )
            if (
                isinstance(by_id_results, list)
                and by_id_results
                and isinstance(by_id_results[0], dict)
            ):
                taxon = by_id_results[0]
                resolved = (
                    get_first_non_whitespace_str(taxon.get("name")) or sci_name or query
                )
                return resolved, taxon

    # if no id (rare), fall back to using the autocomplete result itself
    # (might be partial, but better than nothing)
    if sci_name:
        return sci_name, top

    return None


async def resolve_inat_taxon(query: str, /) -> tuple[str, dict[str, Any]]:
    """Resolve the query to the best-fitting taxon.

    Args:
        query (str): The query to resolve.

    Raises:
        ApiError: If the query is empty after normalization.
        ApiError: If attempting to search iNaturalist yields a non-OK status code.
        ApiError: If there are no search results for the given query.
        ApiError: If the iNaturalist response payload is of an unexpected form.

    Returns:
        tuple[str, dict[str, Any]]: The resolved query
            (scientific name if possible, otherwise the original query) and
            the taxon dictionary from iNaturalist.
    """
    q = normalize_animal_query(query)
    if not q:
        raise ApiError("Animal name cannot be empty")

    # 1) try autocomplete first (best for common names like "dog")
    data = await get_autocomplete_data(q)
    if data is not None:
        return data

    # 2) fallback: regular taxa search
    response = await http_get_json(
        INAT_TAXA_URL,
        params={"q": q, "per_page": AUTOCOMPLETE_MAX_OPTIONS},
        timeout=10,
    )
    if response.status_code != STATUS_OK:
        raise ApiError(
            f"iNaturalist taxa search failed (status {response.status_code})"
        )

    payload = response.json
    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list) or not results:
        raise ApiError(
            f"No iNaturalist results for '{query}'. Try a more specific name."
        )

    taxon = results[0]
    if not isinstance(taxon, dict):
        raise ApiError(f"Unexpected iNaturalist taxa payload for '{query}'")

    scientific_name = get_first_non_whitespace_str(taxon.get("name"))
    resolved = scientific_name or q
    return resolved, taxon


async def fetch_inat_observation_image(taxon_id: int, /) -> str | None:
    """Fetch an observation image for a taxon from iNaturalist.

    Args:
        taxon_id (int): The ID of the taxon to get an image of.

    Returns:
        str | None: The image URL, or None if it can't be found.
    """
    obs_response = await http_get_json(
        INAT_OBSERVATIONS_URL,
        params={
            "taxon_id": taxon_id,
            "per_page": INAT_OBSERVATIONS_IMAGE_FETCH_COUNT,
            "page": 1,
            "order_by": "random",
            "photos": "true",
            "quality_grade": "research",
            "verifiable": "true",
            "captive": "false",
        },
        timeout=10,
    )

    if obs_response.status_code == STATUS_OK:
        obs_json = obs_response.json
        obs_results = obs_json.get("results") if isinstance(obs_json, dict) else None

        if isinstance(obs_results, list) and obs_results:
            # try up to N random observations before giving up
            for _ in range(OBSERVATION_IMAGE_FETCH_ATTEMPTS):
                obs = obs_results[secrets.randbelow(len(obs_results))]
                if not isinstance(obs, dict):
                    continue
                if observation_seems_gross(obs):
                    continue

                photos = obs.get("photos")
                if not isinstance(photos, list) or not photos:
                    continue

                pick = photos[secrets.randbelow(len(photos))]
                if not isinstance(pick, dict):
                    continue

                image_url = extract_inat_photo_url(pick) or extract_inat_photo_url(
                    pick.get("photo")
                )
                if image_url:
                    return image_url

    return None


async def get_wiki_summary_and_url_from_full_taxon(
    taxon_id: int, original_wiki_summary: str | None, original_wiki_url: str | None
) -> tuple[str, str] | tuple[None, None]:
    """Get the wiki summary and URL from a full taxon.

    Args:
        taxon_id (int): The ID of the taxon to search for info of.
        original_wiki_summary (str | None): The original wiki summary data.
        original_wiki_url (str | None): The original wiki URL.

    Returns:
        tuple[str, str] | tuple[None, None]: The new wiki summary and URL.
    """
    taxon_by_id_response = await http_get_json(
        f"{INAT_TAXA_URL}/{taxon_id}",
        timeout=10,
    )
    if taxon_by_id_response.status_code == STATUS_OK:
        by_id_json = taxon_by_id_response.json
        by_id_results = (
            by_id_json.get("results") if isinstance(by_id_json, dict) else None
        )
        if (
            isinstance(by_id_results, list)
            and by_id_results
            and isinstance(by_id_results[0], dict)
        ):
            full_taxon = by_id_results[0]
            return (
                (
                    get_first_non_whitespace_str(full_taxon.get("wikipedia_summary"))
                    or original_wiki_summary
                    or ""
                ),
                (
                    get_first_non_whitespace_str(full_taxon.get("wikipedia_url"))
                    or original_wiki_url
                    or ""
                ),
            )
    return (None, None)


async def _fetch_inat_image(taxon: dict[str, Any], taxon_id: int | None) -> str | None:
    # try getting a good image (prefer observations for randomness)
    # observations first (most random)
    if taxon_id is not None:
        image_url = await fetch_inat_observation_image(taxon_id)
        if image_url:
            return image_url

    # then taxon_photos
    taxon_photos = taxon.get("taxon_photos")
    if isinstance(taxon_photos, list) and taxon_photos:
        photo = taxon_photos[secrets.randbelow(len(taxon_photos))]
        if isinstance(photo, dict):
            return extract_inat_photo_url(photo.get("photo"))

    # lastly default_photo (often constant)
    default_photo = taxon.get("default_photo")
    if isinstance(default_photo, dict):
        return extract_inat_photo_url(default_photo)

    return None


async def fetch_inat_animal(kind: str, /) -> AnimalResult:
    """Fetch an animal from iNaturalist.

    Args:
        kind (str): The kind of animal to search for.

    Raises:
        ApiError: If the animal kind provided has no images on iNaturalist.

    Returns:
        AnimalResult: The result of the search.
    """
    kind = kind.strip().lower()
    resolved_query, taxon = await resolve_inat_taxon(kind)

    taxon_id = taxon.get("id")
    wiki_summary = get_first_non_whitespace_str(taxon.get("wikipedia_summary"))
    wiki_url = get_first_non_whitespace_str(taxon.get("wikipedia_url"))
    preferred_name = get_first_non_whitespace_str(taxon.get("preferred_common_name"))
    scientific_name = get_first_non_whitespace_str(taxon.get("name"))

    image_url = await _fetch_inat_image(
        taxon, taxon_id if isinstance(taxon_id, int) else None
    )
    if not image_url:
        raise ApiError(f"Could not find a photo for '{kind}' on iNaturalist")
    image_url = bump_inat_size(image_url)

    # if wiki summary is missing, fetch the full taxon by id
    if not wiki_summary and isinstance(taxon_id, int):
        wiki_summary, wiki_url = await get_wiki_summary_and_url_from_full_taxon(
            taxon_id, wiki_summary, wiki_url
        )

    # build a fact string (prefer wiki summary, fallback to names)
    fact = clean_wiki_summary(wiki_summary) if wiki_summary else None
    if fact:
        # escape asterisks to make safe for discord formatting
        fact = fact.replace("*", r"\*")
    source = "iNaturalist"
    if wiki_url:
        source = f"iNaturalist (Wiki: {wiki_url})"

    # if user typed a vague thing, the resolved names could help
    if fact and (preferred_name or scientific_name):
        header = " - ".join(
            [name for name in [preferred_name, scientific_name] if name]
        )
        fact = f"**{header}**\n{fact}"
    if fact and resolved_query.lower() != kind.strip().lower():
        fact = f"*Matched:* `{resolved_query}`\n" + fact

    return AnimalResult(
        kind=preferred_name or scientific_name or kind.lower(),
        image_url=image_url,
        fact=fact,
        source=source,
    )


def format_taxon_choice(taxon: dict[str, Any]) -> str | None:
    """Format the taxon choice as a string.

    Args:
        taxon (dict[str, Any]): The taxon data.

    Returns:
        str | None: The formatted string, or None if one cannot be made.
    """
    preferred = get_first_non_whitespace_str(taxon.get("preferred_common_name"))
    sci = get_first_non_whitespace_str(taxon.get("name"))
    rank = get_first_non_whitespace_str(taxon.get("rank"))
    base: str | None

    # ex: Axolotl — Ambystoma mexicanum (species)
    if preferred and sci and preferred.lower() != sci.lower():
        base = f"{preferred} — {sci}"
    else:
        base = preferred or sci

    if not base:
        return None

    if rank:
        base = f"{base} ({rank})"

    if len(base) > AUTOCOMPLETE_LABEL_MAX:
        return base[: AUTOCOMPLETE_LABEL_MAX - 3] + "..."
    return base


async def animal_kind_autocomplete(
    _interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """Get autocomplete results for /animal when a kind is typed in.

    Args:
        current (str): The current value typed in.

    Returns:
        list[app_commands.Choice[str]]: The choices gotten from iNaturalist.
    """
    q = current.strip()
    if len(q) < AUTOCOMPLETE_START_COUNT:
        return []

    cache_key = q.lower()
    if cache_key in autocomplete_cache:
        return autocomplete_cache[cache_key]

    response = await http_get_json(
        INAT_TAXA_AUTOCOMPLETE_URL,
        params={"q": q, "per_page": AUTOCOMPLETE_MAX_OPTIONS},
        timeout=5,
    )

    if response.status_code != STATUS_OK:
        return []

    payload = response.json
    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list):
        return []

    choices: list[app_commands.Choice[str]] = []
    for taxon in results:
        if not isinstance(taxon, dict):
            continue
        label = format_taxon_choice(taxon)
        if not label:
            continue

        # value is what actually gets passed into /animal
        # use scientific name when available because it's unambiguous
        value = get_first_non_whitespace_str(taxon.get("name")) or label
        choices.append(app_commands.Choice(name=label, value=value))

        if len(choices) >= AUTOCOMPLETE_MAX_OPTIONS:
            break

    # cache with simple cap
    if len(autocomplete_cache) >= AUTOCOMPLETE_CACHE_MAX:
        autocomplete_cache.clear()
    autocomplete_cache[cache_key] = choices

    return choices
