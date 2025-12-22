"""Fun commands."""

# TODO modularize into multiple files

from dataclasses import dataclass
import html
from io import BytesIO
import logging
import re
import secrets
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands
from psutil import Process

from ....util.http import STATUS_OK, ApiError, http_get_bytes, http_get_json
from ....util.pawprints import cog_setup_log_msg, log_app_command
from ...info import (
    DEPENDENCIES,
    DISCORD_DOT_PY_VERSION,
    HOST,
    PYTHON_VERSION,
    VERSION,
    get_uptime,
)
from ...interaction import (
    generate_response_embed,
    get_guild_interaction_data,
    report,
    safe_send,
)
from ...ui import COIN_HEADS_COLOR, COIN_TAILS_COLOR
from ...ui.emoji import Status, Visual

_INAT_TAXA_URL = "https://api.inaturalist.org/v1/taxa"
_INAT_OBS_URL = "https://api.inaturalist.org/v1/observations"
_INAT_TAXA_AUTOCOMPLETE_URL = "https://api.inaturalist.org/v1/taxa/autocomplete"

_OBSERVATION_IMAGE_FETCH_ATTEMPTS = 15

_AUTOCOMPLETE_CACHE: dict[str, list[app_commands.Choice[str]]] = {}
_AUTOCOMPLETE_CACHE_MAX = 128
_AUTOCOMPLETE_LABEL_MAX = 100
_AUTOCOMPLETE_START_COUNT = 2
_AUTOCOMPLETE_MAX_OPTIONS = 10

_MAX_FILENAME_LEN = 40

_TAG_RE = re.compile(r"<[^>]+>")

_BAD_WORDS = re.compile(
    r"\b("
    r"skull|skeleton|bones|bone|dead|deceased|roadkill|carcass|corpse|remains|"
    r"taxidermy|pelt|hide|fur|skin|mount|mounted|trophy|"
    r"scat|poop|feces|dropping|tracks|track|footprint|pawprint|"
    r"specimen|museum|collection|preserved|blood"
    r")\b",
    re.IGNORECASE,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _AnimalResult:
    kind: str
    image_url: str
    fact: str | None = None
    source: str | None = None


async def _ensure_full_user(
    client: discord.Client, user: discord.Member | discord.User
) -> discord.User:
    return await client.fetch_user(user.id)


def _safe_filename(filename: str) -> str:
    keep = [c.lower() if c.isalnum() else "_" for c in filename]
    out = "".join(keep).strip("_")

    return out[:_MAX_FILENAME_LEN] or "animal"


def _clean_wiki_summary(text: str) -> str:
    # turn &amp; etc. into real characters
    text = html.unescape(text)
    # remove tags like <b>, <i>, <br>, ...
    text = _TAG_RE.sub("", text)
    # normalize whitespace a bit
    return " ".join(text.split()).strip()


def _first_non_whitespace_str(*values: object) -> str | None:
    for v in values:
        if isinstance(v, str) and v.strip():
            return v
    return None


def _obs_looks_gross(obs: dict[str, Any]) -> bool:
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


def _extract_inat_photo_url(photo_obj: object, /) -> str | None:
    # iNat photos usually look like:
    # {"url": "https://static.inaturalist.org/photos/.../square.jpg?...",
    #  "attribution": "..."}
    if not isinstance(photo_obj, dict):
        return None
    return _first_non_whitespace_str(
        photo_obj.get("url"), photo_obj.get("original_url"), photo_obj.get("large_url")
    )


def _bump_inat_size(url: str, /) -> str:
    # iNat usually returns .../square.jpg, but can be bumped to bigger sizes.
    # this attempts to get the best quality possible, but if it doesn't match
    # it simply returns the url as is.
    return (
        url.replace("/square.", "/large.")
        .replace("/square.jpg", "/large.jpg")
        .replace("/square.jpeg", "/large.jpeg")
        .replace("/square.png", "/large.png")
    )


async def _fetch_inat_observation_image(taxon_id: int, /) -> str | None:
    obs_response = await http_get_json(
        _INAT_OBS_URL,
        params={
            "taxon_id": taxon_id,
            "per_page": 60,
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
                if _obs_looks_gross(obs):
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
                    _first_non_whitespace_str(full_taxon.get("wikipedia_summary"))
                    or original_wiki_summary
                    or ""
                ),
                (
                    _first_non_whitespace_str(full_taxon.get("wikipedia_url"))
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

    # if no photo, fall back to observations

    return None


async def _fetch_inat_animal(kind: str, /) -> _AnimalResult:
    q = kind.strip()
    if not q:
        raise ApiError("Animal name cannot be empty")

    # find best matching taxon
    taxa_response = await http_get_json(
        _INAT_TAXA_URL, params={"q": q, "per_page": 5}, timeout=10
    )
    if taxa_response.status_code != STATUS_OK:
        raise ApiError(
            f"iNaturalist taxa search failed (status {taxa_response.status_code})"
        )

    taxa_json = taxa_response.json
    results = taxa_json.get("results") if isinstance(taxa_json, dict) else None
    if not isinstance(results, list) or not results:
        raise ApiError(
            f"No iNaturalist results for '{kind}'. Please try a different query."
        )

    taxon = results[0]
    if not isinstance(taxon, dict):
        raise ApiError(f"Unexpected iNaturalist taxa payload for '{kind}'")

    taxon_id = taxon.get("id")
    wiki_summary = _first_non_whitespace_str(taxon.get("wikipedia_summary"))
    wiki_url = _first_non_whitespace_str(taxon.get("wikipedia_url"))
    preferred_name = _first_non_whitespace_str(taxon.get("preferred_common_name"))
    scientific_name = _first_non_whitespace_str(taxon.get("name"))

    image_url = await _fetch_inat_image(
        taxon, taxon_id if isinstance(taxon_id, int) else None
    )
    if not image_url:
        raise ApiError(f"Could not find a photo for '{kind}' on iNaturalist")
    image_url = _bump_inat_size(image_url)

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
        source = f"iNaturalist (Wiki: {wiki_url})"

    # if user typed a vague thing, the resolved names could help
    if fact and (preferred_name or scientific_name):
        header = " - ".join(
            [name for name in [preferred_name, scientific_name] if name]
        )
        fact = f"**{header}**\n{fact}"

    return _AnimalResult(
        kind=preferred_name or scientific_name or kind.lower(),
        image_url=image_url,
        fact=fact,
        source=source,
    )


async def _fetch_animal(kind: str, /) -> _AnimalResult:
    kind = kind.strip().lower()
    return await _fetch_inat_animal(kind)


async def _send_animal_embed(
    interaction: discord.Interaction, /, result: _AnimalResult, *, emoji: str
) -> None:
    image_bytes = await http_get_bytes(result.image_url, timeout=10)
    image_fp = BytesIO(image_bytes)
    filename = f"{_safe_filename(result.kind)}.png"
    file = discord.File(fp=image_fp, filename=filename)

    description_parts = []
    if result.fact:
        description_parts.append(result.fact)
    if result.source:
        description_parts.append(f"*Source: {result.source}*")

    embed, icon = generate_response_embed(
        title=f"{emoji} Random {result.kind.title()}",
        description="\n\n".join(description_parts)
        if description_parts
        else "Here you go!",
    )
    embed.set_image(url=f"attachment://{filename}")

    await safe_send(interaction, embed=embed, files=(file, icon))


def _format_taxon_choice(taxon: dict[str, Any]) -> str | None:
    preferred = _first_non_whitespace_str(taxon.get("preferred_common_name"))
    sci = _first_non_whitespace_str(taxon.get("name"))
    rank = _first_non_whitespace_str(taxon.get("rank"))
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


async def _animal_kind_autocomplete(
    _interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    q = current.strip()
    if len(q) < _AUTOCOMPLETE_START_COUNT:
        return []

    cache_key = q.lower()
    if cache_key in _AUTOCOMPLETE_CACHE:
        return _AUTOCOMPLETE_CACHE[cache_key]

    resp = await http_get_json(
        _INAT_TAXA_AUTOCOMPLETE_URL,
        params={"q": q, "per_page": _AUTOCOMPLETE_MAX_OPTIONS},
        timeout=5,
    )

    if resp.status_code != STATUS_OK:
        return []

    payload = resp.json
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
        value = _first_non_whitespace_str(taxon.get("name")) or label
        choices.append(app_commands.Choice(name=label, value=value))

        if len(choices) >= _AUTOCOMPLETE_MAX_OPTIONS:
            break

    # cache with simple cap
    if len(_AUTOCOMPLETE_CACHE) >= _AUTOCOMPLETE_CACHE_MAX:
        _AUTOCOMPLETE_CACHE.clear()
    _AUTOCOMPLETE_CACHE[cache_key] = choices

    return choices


class FunCog(commands.Cog, name="Fun Commands"):
    """Cog containing fun commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Create the FunCog.

        Args:
            bot (commands.Bot): The bot to load the cog to.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Run when the cog is ready to be used."""
        cog_setup_log_msg(type(self).__name__, self.bot)

    @app_commands.command(name="stats", description="Get stats about CatBot")
    async def stats(self, interaction: discord.Interaction) -> None:
        """Report stats about CatBot."""
        log_app_command(interaction)

        await interaction.response.defer(thinking=True)

        guilds = str(len(self.bot.guilds))
        memory_mb = Process().memory_info().rss / (1024**2)

        embed, icon = generate_response_embed(
            title=f"{Visual.CHART} CatBot Stats",
            description="Here's some statistics about myself.",
        )
        embed.add_field(name="Version", value=VERSION)
        embed.add_field(name="# of Guilds", value=guilds)
        embed.add_field(
            name="Uptime",
            value=get_uptime(),
            inline=False,
        )
        embed.add_field(name="Language", value=f"Python {PYTHON_VERSION}")
        embed.add_field(name="Memory Usage", value=f"{memory_mb:.2f} MB")
        embed.add_field(name="Package", value=f"discord.py {DISCORD_DOT_PY_VERSION}")
        embed.add_field(name="Dependencies", value=DEPENDENCIES)
        embed.add_field(name="Host", value=HOST, inline=False)

        await safe_send(interaction, embed=embed, file=icon)

    @app_commands.command(name="coinflip", description="Flip a coin (50/50 odds)")
    async def coin_flip(self, interaction: discord.Interaction) -> None:
        """Flip a coin, returning an embed with custom coin images."""
        log_app_command(interaction)

        title = f"{Visual.COIN} Coin Flip"
        description = "Here's the result of your coin flip."

        heads = secrets.randbelow(2)  # 0 or 1
        if heads:
            embed, icon = generate_response_embed(
                title=title, description=description, color=COIN_HEADS_COLOR
            )
            coin = discord.File(fp="static/images/coin_heads.png", filename="coin.png")
        else:
            embed, icon = generate_response_embed(
                title=title, description=description, color=COIN_TAILS_COLOR
            )
            coin = discord.File(fp="static/images/coin_tails.png", filename="coin.png")

        embed.set_image(url="attachment://coin.png")

        await safe_send(interaction, embed=embed, files=(coin, icon), ephemeral=False)

    @app_commands.command(name="profile", description="Get a user's profile picture")
    @app_commands.describe(user="User to get the profile picture of")
    async def profile(
        self,
        interaction: discord.Interaction,
        user: discord.Member | discord.User | None = None,
    ) -> None:
        """Get a user's profile picture."""
        log_app_command(interaction)

        interaction_user = interaction.user
        target = user or interaction_user
        display_name = target.display_name

        embed, icon = generate_response_embed(
            title=f"{Visual.PHOTO} {display_name}'s Profile Picture",
            description=f"Here's {display_name}'s profile picture.",
        )
        embed.set_image(url=target.display_avatar.url)

        await interaction.response.send_message(embed=embed, file=icon)

    @app_commands.command(name="banner", description="Get a user's profile banner")
    @app_commands.describe(user="User to get the profile banner of")
    async def banner(
        self,
        interaction: discord.Interaction,
        user: discord.Member | discord.User | None = None,
    ) -> None:
        """Get a user's profile banner."""
        log_app_command(interaction)

        target = user or interaction.user
        # get the full user payload to ensure it has the banner info
        full_user = await _ensure_full_user(interaction.client, target)

        if full_user.banner is None:
            await report(
                interaction,
                f"{full_user.display_name} does not have a banner.",
                Status.FAILURE,
            )
            return

        display_name = full_user.display_name

        embed, icon = generate_response_embed(
            title=f"{Visual.PHOTO} {display_name}'s Profile Banner",
            description=f"Here's {display_name}'s profile banner.",
        )
        embed.set_image(url=full_user.banner.url)

        await interaction.response.send_message(embed=embed, file=icon)

    @app_commands.autocomplete(kind=_animal_kind_autocomplete)
    @app_commands.command(
        name="animal", description="Get an animal picture (and maybe a fact)!"
    )
    @app_commands.describe(
        kind="Which animal to fetch (type your animal, "
        "then wait for the autocomplete and pick the best-fitting option)"
    )
    async def animal(self, interaction: discord.Interaction, kind: str) -> None:
        """Get a random animal image and possibly a fact."""
        log_app_command(interaction)

        await interaction.response.defer(thinking=True)

        try:
            result = await _fetch_animal(kind)
            await _send_animal_embed(interaction, result, emoji=Visual.PAWS)
        except ApiError as e:
            logger.warning("Animal API error: %s", e)
            await report(
                interaction,
                f"{e}\nPlease try again later, or submit a "
                "bug report if this keeps happening.",
                Status.ERROR,
            )
        except Exception:
            logger.exception("Unexpected error in /animal")
            await report(
                interaction,
                "Something went wrong.\nPlease try again later, or submit a "
                "bug report if this keeps happening.",
                Status.ERROR,
            )

    @app_commands.command(
        name="members", description="Get data regarding the members in this server"
    )
    async def members(self, interaction: discord.Interaction) -> None:
        """Get member info."""
        log_app_command(interaction)

        data = get_guild_interaction_data(interaction)
        if data is None:
            await report(
                interaction,
                "This command can only be used in a server!",
                Status.FAILURE,
            )
            return

        guild = data.guild
        members = guild.members
        member_count = guild.member_count
        if member_count is None:
            await report(
                interaction,
                "Could not fetch member info, please try again later.",
                Status.WARNING,
            )
            return

        human_members = len([member for member in members if not member.bot])
        online_members = len(
            [member for member in members if str(member.status) != "offline"]
        )

        embed, icon = generate_response_embed(
            title=f"{Visual.PEOPLE_SYMBOL} {guild.name} Member Count",
            description="Here's the member count for this server.",
        )
        embed.add_field(
            name="Total Members",
            value=member_count,
            inline=False,
        )
        embed.add_field(name="Human Members", value=human_members, inline=False)
        embed.add_field(
            name="Bot Members",
            value=member_count - human_members,
            inline=False,
        )
        embed.add_field(name="Online Members", value=online_members, inline=False)
        embed.add_field(
            name="Offline Members",
            value=member_count - online_members,
            inline=False,
        )

        await interaction.response.send_message(embed=embed, file=icon)


async def setup(bot: commands.Bot) -> None:
    """Set up the cog."""
    await bot.add_cog(FunCog(bot))
