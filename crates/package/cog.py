import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from django.utils import timezone

from ballsdex.core.utils import checks
from bd_models.models import Player

from ..models import CrateInstance, PlayerPoolCooldown, Pool, get_settings
from .core.crate import get_random_crate
from .core.utils.format import format_content
from .core.utils.transformers import CrateTransform
from .core.views import CrateListView

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger("crates.package.cog")


class Crates(commands.GroupCog):
    """
    Crate package commands.
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot

    admin = app_commands.Group(name="admin", description="admin crate management")

    async def _claim(self, interaction, *, pool_name: str):
        await interaction.response.defer(ephemeral=True)

        settings = await get_settings()

        pool = await Pool.objects.filter(name=pool_name, enabled=True).afirst()

        if not pool:
            await interaction.followup.send(f"{pool_name} is currently disabled.")
            return

        player, _ = await Player.objects.aget_or_create(discord_id=interaction.user.id)
        cooldown, _ = await PlayerPoolCooldown.objects.select_related("pool").aget_or_create(
            player=player, pool=pool, defaults={"last_claimed": timezone.now() - pool.cooldown}
        )

        if not cooldown.can_claim():
            available_at = cooldown.available_at()
            await interaction.followup.send(
                f"You've already claimed from {pool_name.lower()}. Try again <t:{int(available_at.timestamp())}:R>."
            )
            return

        crate = await get_random_crate(pool_name=pool_name)

        if not crate:
            await interaction.followup.send(
                f"There are no {settings.plural_crate_name} in {pool_name.lower()} right now."
            )
            return

        await CrateInstance.objects.acreate(player=player, crate=crate)

        cooldown.last_claimed = timezone.now()
        await cooldown.asave(update_fields=("last_claimed",))

        await interaction.followup.send(
            await format_content(settings.claim_message, name=crate.name, pool=pool_name.lower())
        )

    @app_commands.command()
    async def list(self, interaction: discord.Interaction["BallsDexBot"]):
        """
        Displays all your crates.
        """
        await interaction.response.send_message(view=await CrateListView.build(interaction.user))

    @app_commands.command()
    async def daily(self, interaction: discord.Interaction["BallsDexBot"]):
        """
        Claims a crate for the current day.
        """
        await self._claim(interaction, pool_name="Daily")

    @app_commands.command()
    async def weekly(self, interaction: discord.Interaction["BallsDexBot"]):
        """
        Claims a crate for the current week.
        """
        await self._claim(interaction, pool_name="Weekly")

    @admin.command()
    @checks.app_check(checks.has_permissions("crates.add_crateinstance"))
    async def give(self, interaction: discord.Interaction["BallsDexBot"], user: discord.User, crate: CrateTransform):
        """
        Gives a crate to a user.

        Parameters
        ----------
        user: discord.User
            The user you want to give a crate to.
        crate: Crate
            The crate you want to give.
        """
        await interaction.response.defer(ephemeral=True)

        settings = await get_settings()
        player, _ = await Player.objects.aget_or_create(discord_id=user.id)

        await CrateInstance.objects.acreate(player=player, crate=crate)

        log.info(
            f"{interaction.user.name} gave one '{crate}' {settings.crate_name} to {user.name}.", extra={"webhook": True}
        )
        await interaction.followup.send(f"Gave one **{crate}** {settings.crate_name} to {user.mention}.")

    @admin.command()
    @checks.app_check(checks.has_permissions("crates.view_crateinstance"))
    async def view(self, interaction: discord.Interaction["BallsDexBot"], user: discord.User):
        """
        Displays a list of a user's crates.

        Parameters
        ----------
        user: discord.User
            The user you want to view crates from.
        """
        await interaction.response.defer(ephemeral=True)

        settings = await get_settings()
        player = await Player.objects.aget_or_none(discord_id=user.id)

        if not player:
            await interaction.followup.send(f"{user.mention} has no {settings.plural_crate_name} to view.")
            return

        await interaction.followup.send(view=await CrateListView.build(user, interaction.user))
