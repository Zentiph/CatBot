"""Tools for interacting with the iNaturalist API for the /animal command."""

from dataclasses import dataclass
import html
import re
import secrets
from typing import Any, Literal

import discord
from discord import app_commands

from .....util.http import STATUS_OK, ApiError, http_get_json

__author__ = "Gavin Borne"
__license__ = "MIT"

ImageFetchAmount = Literal[1, 2, 3, 4, 5]

_INAT_TAXA_URL = "https://api.inaturalist.org/v1/taxa"
_INAT_OBSERVATIONS_URL = "https://api.inaturalist.org/v1/observations"
_INAT_TAXA_AUTOCOMPLETE_URL = "https://api.inaturalist.org/v1/taxa/autocomplete"

_INAT_OBSERVATIONS_IMAGE_FETCH_COUNT = 60
_OBSERVATION_IMAGE_FETCH_ATTEMPTS = 15

_AUTOCOMPLETE_MAX_OPTIONS = 10
_AUTOCOMPLETE_LABEL_MAX = 100
_AUTOCOMPLETE_CACHE_MAX = 128
_AUTOCOMPLETE_START_COUNT = 3

# the very first time i tested /animal with randomized images i got a photo
# of a dog's skull...
# SO here we are!!
_BAD_WORDS = re.compile(
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

_HTML_TAG_RE = re.compile(r"<[^>]+>")

_autocomplete_cache: dict[str, list[app_commands.Choice[str]]] = {}


@dataclass(frozen=True)
class AnimalResult:
    """The result of an animal search."""

    kind: str
    """The kind of animal."""
    image_url: str
    """The URL to the image found."""
    images: list[str]
    """The images obtained."""
    fact: str | None = None
    """A fact blurb about the animal."""
    source: str | None = None
    """The source of the animal and fact."""


def _get_first_non_whitespace_str(*values: object) -> str | None:
    for v in values:
        if isinstance(v, str) and v.strip():
            return v
    return None


def _clean_wiki_summary(text: str) -> str:
    # turn &amp; etc. into real characters
    text = html.unescape(text)
    # remove tags like <b>, <i>, <br>, ...
    text = _HTML_TAG_RE.sub("", text)
    # normalize whitespace a bit
    return " ".join(text.split()).strip()


def _extract_inat_photo_url(photo_obj: object, /) -> str | None:
    # iNat photos usually look like:
    # {"url": "https://static.inaturalist.org/photos/.../square.jpg?...",
    #  "attribution": "..."}
    if not isinstance(photo_obj, dict):
        return None
    return _get_first_non_whitespace_str(
        photo_obj.get("url"), photo_obj.get("original_url"), photo_obj.get("large_url")
    )


def _observation_seems_gross(obs: dict[str, Any]) -> bool:
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
    return bool(_BAD_WORDS.search(haystack))


async def _get_autocomplete_data(query: str, /) -> tuple[str, dict[str, Any]] | None:
    autocomplete_response = await http_get_json(
        _INAT_TAXA_AUTOCOMPLETE_URL,
        params={"q": query, "per_page": _AUTOCOMPLETE_MAX_OPTIONS},
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
    sci_name = _get_first_non_whitespace_str(top.get("name"))

    # prefer fetching full taxon by id for consistent fields
    if isinstance(taxon_id, int):
        by_id = await http_get_json(f"{_INAT_TAXA_URL}/{taxon_id}", timeout=10)
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
                    _get_first_non_whitespace_str(taxon.get("name"))
                    or sci_name
                    or query
                )
                return resolved, taxon

    # if no id (rare), fall back to using the autocomplete result itself
    # (might be partial, but better than nothing)
    if sci_name:
        return sci_name, top

    return None


async def _resolve_inat_taxon(query: str, /) -> tuple[str, dict[str, Any]]:
    q = " ".join(query.strip().split())  # normalize query
    if not q:
        raise ApiError("Animal name cannot be empty")

    # 1) try autocomplete first (best for common names like "dog")
    data = await _get_autocomplete_data(q)
    if data is not None:
        return data

    # 2) fallback: regular taxa search
    response = await http_get_json(
        _INAT_TAXA_URL,
        params={"q": q, "per_page": _AUTOCOMPLETE_MAX_OPTIONS},
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

    scientific_name = _get_first_non_whitespace_str(taxon.get("name"))
    resolved = scientific_name or q
    return resolved, taxon


async def _fetch_inat_observation_image(taxon_id: int, /) -> str | None:
    obs_response = await http_get_json(
        _INAT_OBSERVATIONS_URL,
        params={
            "taxon_id": taxon_id,
            "per_page": _INAT_OBSERVATIONS_IMAGE_FETCH_COUNT,
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
            for _ in range(_OBSERVATION_IMAGE_FETCH_ATTEMPTS):
                obs = obs_results[secrets.randbelow(len(obs_results))]
                if not isinstance(obs, dict):
                    continue
                if _observation_seems_gross(obs):
                    continue

                photos = obs.get("photos")
                if not isinstance(photos, list) or not photos:
                    continue

                pick = photos[secrets.randbelow(len(photos))]
                if not isinstance(pick, dict):
                    continue

                image_url = _extract_inat_photo_url(pick) or _extract_inat_photo_url(
                    pick.get("photo")
                )
                if image_url:
                    return image_url

    return None


async def _get_wiki_summary_and_url_from_full_taxon(
    taxon_id: int, original_wiki_summary: str | None, original_wiki_url: str | None
) -> tuple[str, str] | tuple[None, None]:
    taxon_by_id_response = await http_get_json(
        f"{_INAT_TAXA_URL}/{taxon_id}",
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
                    _get_first_non_whitespace_str(full_taxon.get("wikipedia_summary"))
                    or original_wiki_summary
                    or ""
                ),
                (
                    _get_first_non_whitespace_str(full_taxon.get("wikipedia_url"))
                    or original_wiki_url
                    or ""
                ),
            )
    return (None, None)


async def _fetch_inat_image(taxon: dict[str, Any], taxon_id: int | None) -> str | None:
    # try getting a good image (prefer observations for randomness)
    # observations first (most random)
    if taxon_id is not None:
        image_url = await _fetch_inat_observation_image(taxon_id)
        if image_url:
            return image_url

    # then taxon_photos
    taxon_photos = taxon.get("taxon_photos")
    if isinstance(taxon_photos, list) and taxon_photos:
        photo = taxon_photos[secrets.randbelow(len(taxon_photos))]
        if isinstance(photo, dict):
            return _extract_inat_photo_url(photo.get("photo"))

    # lastly default_photo (often constant)
    default_photo = taxon.get("default_photo")
    if isinstance(default_photo, dict):
        return _extract_inat_photo_url(default_photo)

    return None


async def _fetch_inat_images(
    taxon: dict[str, Any], taxon_id: int | None, images: int = 1
) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    # try multiple pulls
    # might repeat images
    attempts = images * 6

    for _ in range(attempts):
        url = await _fetch_inat_image(
            taxon, taxon_id if isinstance(taxon_id, int) else None
        )
        if not url:
            continue

        # iNat usually returns .../square.jpg, but can be bumped to bigger sizes
        url = (
            url.replace("/square.", "/large.")
            .replace("/square.jpg", "/large.jpg")
            .replace("/square.jpeg", "/large.jpeg")
            .replace("/square.png", "/large.png")
        )

        if url in seen:
            continue
        seen.add(url)
        urls.append(url)
        if len(urls) >= images:
            break

    return urls


async def fetch_inat_animal(
    kind: str, /, *, images: ImageFetchAmount = 1
) -> AnimalResult:
    """Fetch an animal from iNaturalist.

    Args:
        kind (str): The kind of animal to search for.
        images (ImageFetchAmount, optional): The number of images to fetch.
            Defaults to 1.

    Raises:
        ApiError: If the animal kind provided has no images on iNaturalist.

    Returns:
        AnimalResult: The result of the search.
    """
    kind = kind.strip().lower()
    resolved_query, taxon = await _resolve_inat_taxon(kind)

    taxon_id = taxon.get("id")
    wiki_summary = _get_first_non_whitespace_str(taxon.get("wikipedia_summary"))
    wiki_url = _get_first_non_whitespace_str(taxon.get("wikipedia_url"))
    preferred_name = _get_first_non_whitespace_str(taxon.get("preferred_common_name"))
    scientific_name = _get_first_non_whitespace_str(taxon.get("name"))

    urls = await _fetch_inat_images(
        taxon, taxon_id if isinstance(taxon_id, int) else None, images
    )
    if not urls:
        raise ApiError(f"Could not find a photo for '{kind}' on iNaturalist")

    # if wiki summary is missing, fetch the full taxon by id
    if not wiki_summary and isinstance(taxon_id, int):
        wiki_summary, wiki_url = await _get_wiki_summary_and_url_from_full_taxon(
            taxon_id, wiki_summary, wiki_url
        )

    # build a fact string (prefer wiki summary, fallback to names)
    fact = _clean_wiki_summary(wiki_summary) if wiki_summary else None
    if fact:
        # escape asterisks to make safe for discord formatting
        fact = fact.replace("*", r"\*")
    source = "iNaturalist"
    if wiki_url:
        # normalize URL to prevent discord formatting with spaces and breaking the link
        source = f"iNaturalist (Wiki: {wiki_url.replace('%20', '_').replace(' ', '_')})"

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
        image_url=urls[0],
        images=urls,
        fact=fact,
        source=source,
    )


def _format_taxon_choice(taxon: dict[str, Any]) -> str | None:
    preferred = _get_first_non_whitespace_str(taxon.get("preferred_common_name"))
    sci = _get_first_non_whitespace_str(taxon.get("name"))
    rank = _get_first_non_whitespace_str(taxon.get("rank"))
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

    if len(base) > _AUTOCOMPLETE_LABEL_MAX:
        return base[: _AUTOCOMPLETE_LABEL_MAX - 3] + "..."
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
    if len(q) < _AUTOCOMPLETE_START_COUNT:
        return []

    cache_key = q.lower()
    if cache_key in _autocomplete_cache:
        return _autocomplete_cache[cache_key]

    response = await http_get_json(
        _INAT_TAXA_AUTOCOMPLETE_URL,
        params={"q": q, "per_page": _AUTOCOMPLETE_MAX_OPTIONS},
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
        label = _format_taxon_choice(taxon)
        if not label:
            continue

        # value is what actually gets passed into /animal
        # use scientific name when available because it's unambiguous
        value = _get_first_non_whitespace_str(taxon.get("name")) or label
        choices.append(app_commands.Choice(name=label, value=value))

        if len(choices) >= _AUTOCOMPLETE_MAX_OPTIONS:
            break

    # cache with simple cap
    if len(_autocomplete_cache) >= _AUTOCOMPLETE_CACHE_MAX:
        _autocomplete_cache.clear()
    _autocomplete_cache[cache_key] = choices

    return choices
