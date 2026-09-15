from contextlib import suppress
from typing import TYPE_CHECKING

import discord
from django.db.models import Count, Prefetch

from ballsdex.core.discord import LayoutView
from bd_models.models import BallInstance, Player

from ...models import Crate, CrateInstance, get_settings
from ..core.crate import open_crate
from .shared import BaseResultView, MenuContainer

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

__all__ = ("CrateListView",)


class OpenButton(discord.ui.Button):
    def __init__(self, crate_instance: CrateInstance):
        super().__init__(label="Open")

        self.crate_instance_id = crate_instance.pk
        self.disabled = not crate_instance.crate.openable

    async def callback(self, interaction: discord.Interaction["BallsDexBot"]):
        await interaction.response.defer()

        settings = await get_settings()
        player, _ = await Player.objects.aget_or_create(discord_id=interaction.user.id)

        try:
            crate_instance = await CrateInstance.objects.select_related("player", "crate").aget(
                pk=self.crate_instance_id
            )
        except CrateInstance.DoesNotExist:
            crate_instance = None

        if not crate_instance or crate_instance.player != player:
            await interaction.followup.send(f"This {settings.crate_name} no longer belongs to you.")

            return

        deleted_count, _ = await CrateInstance.objects.filter(pk=self.crate_instance_id, player=player).adelete()

        if deleted_count == 0:
            await interaction.followup.send(f"This {settings.crate_name} has already been opened.")

            return

        instances = await open_crate(crate_instance, player)

        await interaction.followup.send(
            view=await CrateResultView.build(interaction.client, interaction.user, crate_instance, instances)
        )

        with suppress(discord.HTTPException, discord.NotFound):
            await interaction.edit_original_response(
                view=await CrateListView.build(interaction.client, interaction.user)
            )


class CrateResultView(BaseResultView):
    @classmethod
    async def build(
        cls,
        bot: "BallsDexBot",
        author: discord.User | discord.Member,
        crate_instance: CrateInstance,
        instances: list[BallInstance],
    ):
        settings = await get_settings()
        items = []

        for instance in instances:
            ball_emoji = bot.get_emoji(instance.countryball.emoji_id) or "?"
            special_emoji = f"{instance.special.emoji} " if instance.special else ""

            items.append(f"{special_emoji}{ball_emoji} **{instance.countryball.country}** (`#{instance.pk:x}`)")

        return await cls.build_view(author, f"{crate_instance.crate} {settings.crate_name.title()} Results", items)


class CrateListView(LayoutView):
    def __init__(self, viewer: discord.User | discord.Member):
        super().__init__()
        self.viewer = viewer
        self.restrict_author(viewer.id)

    @classmethod
    async def build(
        cls,
        bot: "BallsDexBot",
        user: discord.User | discord.Member,
        viewer: discord.User | discord.Member | None = None,
    ) -> "CrateListView":
        viewer = viewer or user
        settings = await get_settings()
        player, _ = await Player.objects.aget_or_create(discord_id=user.id)

        crates = [
            crate
            async for crate in Crate.objects.filter(instances__player=player)
            .annotate(count=Count("instances"))
            .order_by("-count")
            .prefetch_related(
                Prefetch("instances", queryset=CrateInstance.objects.filter(player=player), to_attr="player_instances")
            )
        ]

        view = cls(viewer)
        components: list[discord.ui.Section | discord.ui.TextDisplay] = []

        for crate in crates:
            text_item = discord.ui.TextDisplay(f"**{await crate.describe(bot)}** ({crate.count})")

            if user != viewer:
                components.append(text_item)
                continue

            components.append(discord.ui.Section(text_item, accessory=OpenButton(crate.player_instances[0])))

        if not components:
            components.append(discord.ui.TextDisplay(f"*No {settings.plural_crate_name} found*"))

        container = await MenuContainer.build(
            discord.ui.TextDisplay(f"### {user.display_name} {settings.plural_crate_name.title()}"),
            discord.ui.Separator(),
            *components,
        )

        view.add_item(container)

        return view
