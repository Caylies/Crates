import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from django.utils import timezone

from ballsdex.core.utils import checks
from bd_models.models import Player

from ..models import CrateInstance, PlayerPoolCooldown, Pool, get_settings
from .core.pool import evaluate_pool, give_pool_crates
from .core.utils.transformers import CrateTransform
from .views import CrateListView, PoolResultView

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger("crates.package.cog")


class Crates(commands.GroupCog):
    """
    Crate package commands.
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        self._pool_command_names: set[str] = set()

    admin = app_commands.Group(name="admin", description="admin crate management")

    async def cog_load(self) -> None:
        await self._register_pool_commands()

    async def cog_unload(self) -> None:
        if not self.app_command:
            raise

        self.bot.tree.remove_command(self.app_command.name)

    def _build_pool_command(self, pool: Pool) -> app_commands.Command:

        async def callback(interaction: discord.Interaction["BallsDexBot"]) -> None:
            await self._claim(interaction, pool)

        return app_commands.Command(name=pool.command_name, description=pool.command_description, callback=callback)

    async def _register_pool_commands(self):
        if not self.app_command:
            return

        for name in self._pool_command_names:
            self.app_command.remove_command(name)

        self._pool_command_names = set()

        async for pool in Pool.objects.filter(enabled=True):
            self.app_command.add_command(self._build_pool_command(pool))
            self._pool_command_names.add(pool.command_name)

    async def _claim(self, interaction, pool: Pool):
        await interaction.response.defer(ephemeral=True)

        settings = await get_settings()
        player, _ = await Player.objects.aget_or_create(discord_id=interaction.user.id)

        cooldown, _ = await PlayerPoolCooldown.objects.select_related("pool").aget_or_create(
            player=player, pool=pool, defaults={"last_claimed": timezone.now() - pool.cooldown}
        )

        if not cooldown.can_claim():
            available_at = cooldown.available_at()

            await interaction.followup.send(
                f"You've already claimed from {pool.name.lower()}. Try again <t:{int(available_at.timestamp())}:R>."
            )

            return

        condition_result = await evaluate_pool(pool, bot=self.bot, user=interaction.user, player=player)

        if not condition_result.passed:
            failures_list = " _**OR**_\n".join(f"- {message}" for message in condition_result.failures)

            await interaction.followup.send(
                f"You do not meet the required criteria to claim from {pool.name.lower()}.\n\n{failures_list}"
            )

            return

        instances = await give_pool_crates(player, pool)

        if not instances:
            await interaction.followup.send(
                f"There are no {settings.plural_crate_name} in {pool.name.lower()} right now."
            )

            return

        cooldown.last_claimed = timezone.now()
        await cooldown.asave(update_fields=("last_claimed",))

        await interaction.followup.send(view=await PoolResultView.build(self.bot, interaction.user, pool, instances))

    @app_commands.command()
    async def list(self, interaction: discord.Interaction["BallsDexBot"]):
        """
        Displays all your crates.
        """
        await interaction.response.send_message(view=await CrateListView.build(self.bot, interaction.user))

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

    @commands.command()
    async def reloadcrates(self, ctx: commands.Context["BallsDexBot"]):
        message = await ctx.send("Reloading Crates package...")

        await self._register_pool_commands()
        await message.reply("Reloaded Crates")
