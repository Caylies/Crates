import logging
from typing import TYPE_CHECKING

import discord
from query_builder_widget import use_operator

from bd_models.models import BallInstance, Player, balls
from settings.models import settings

from ....models import CrateInstance, get_settings
from ..utils.discord import user_in_guild

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger("crates.package.core.pool.checks")

_OPERATOR_PHRASES = {
    "equals": "exactly",
    "not_equals": "anything other than",
    "greater": "more than",
    "greater_or_equal": "at least",
    "less": "less than",
    "less_or_equal": "at most",
}


def _format_requirement(operator: str, expected: str, suffix: str = "") -> str:
    phrase = _OPERATOR_PHRASES.get(operator, operator.replace("_", " "))

    return f"{phrase} {expected}{suffix}"


def _format_operator(operator: str) -> str:
    formatted_operator = operator.replace("_", " ")
    connector = "than" if formatted_operator in ("greater", "less") else "to"

    if formatted_operator in ("equals", "not_equals"):
        formatted_operator = formatted_operator[:-1]

    return f"{formatted_operator} {connector}"


async def in_guild(bot: "BallsDexBot", user: discord.User, expected: str, operator: str):
    guild = bot.get_guild(int(expected))

    if not guild:
        log.error(
            f"While validating a 'Server' pool rule, failed to get server with ID: `{expected}`",
            extra={"webhook": True},
        )

        not_text = "not " if operator == "not_equals" else " "

        return False, f"Must {not_text}be in the specified server"

    condition = await user_in_guild(bot, user, guild)

    match operator:
        case "equals":
            return condition, f"Must be in the *{guild.name}* server"

        case "not_equals":
            return not condition, f"Must not be in the *{guild.name}* server"


async def has_ball_completion(player: Player, expected: str, operator: str):
    bot_countryballs = [ball for ball in balls.values() if ball.enabled]

    owned_countryballs = set(
        [ball async for ball in BallInstance.objects.filter(player=player).distinct().values_list("ball_id", flat=True)]
    )

    completion = round(len(owned_countryballs) / len(bot_countryballs) * 100, 1)
    result = use_operator(operator, completion, int(expected))

    if not result:
        formatted_operator = _format_operator(operator)

        return False, f"{settings.collectible_name.title()} completion must be {formatted_operator} {expected}%"

    return True


async def has_ball_count(player: Player, expected: str, operator: str):
    count = await BallInstance.objects.filter(player=player).acount()
    result = use_operator(operator, count, int(expected))

    if not result:
        formatted_operator = _format_operator(operator)

        return False, f"{settings.collectible_name.title()} count must be {formatted_operator} {expected}"

    return True


async def is_user(user: discord.User, expected: str, operator: str):
    result = use_operator(operator, user.id, int(expected))

    if not result:
        return False, "Must be the correct user to claim"

    return True


async def has_crate_count(player: Player, expected: str, operator: str):
    count = await CrateInstance.objects.filter(player=player).acount()
    expected_count = int(expected)

    if use_operator(operator, count, expected_count):
        return True

    crates_settings = await get_settings()
    requirement = _format_requirement(operator, expected)

    required_name = crates_settings.crate_name_for(expected_count)
    current_name = crates_settings.crate_name_for(count)

    return False, f"You must have {requirement} {required_name}, but you currently have {count} {current_name}."
