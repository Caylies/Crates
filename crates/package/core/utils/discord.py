from contextlib import suppress
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def user_in_guild(bot: "BallsDexBot", user: discord.User, guild: discord.Guild) -> bool:
    """
    Checks if a user is in a guild. Avoids an HTTP request if member intent is enabled.
    """

    if bot.intents.members:
        member = guild.get_member(user.id)

        return member is not None

    with suppress(discord.NotFound, discord.HTTPException):
        member = await guild.fetch_member(user.id)

        return member is not None

    return False
