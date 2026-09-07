from contextlib import suppress
from typing import TYPE_CHECKING

import discord
from django.db.models import Count, Prefetch

from ballsdex.core.discord import LayoutView
from bd_models.models import BallInstance, Player

from ...models import Crate, CrateInstance, get_settings
from .crate import open_crate

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


class MenuContainer(discord.ui.Container):
    def __init__(self, *children: discord.ui.Item, accent_color: discord.Color | None = None):
        super().__init__(*children, accent_color=accent_color)

    @classmethod
    async def build(cls, *children: discord.ui.Item) -> "MenuContainer":
        settings = await get_settings()
        accent_color = None

        if settings.menu_color:
            color_str = settings.menu_color if settings.menu_color.startswith("#") else f"#{settings.menu_color}"
            accent_color = discord.Color.from_str(color_str)

        return cls(*children, accent_color=accent_color)


class OpenButton(discord.ui.Button):
    def __init__(self, crate_instance: CrateInstance):
        super().__init__(label="Open")
        self.crate_instance = crate_instance

    async def callback(self, interaction: discord.Interaction["BallsDexBot"]):
        await interaction.response.defer()

        settings = await get_settings()
        player, _ = await Player.objects.aget_or_create(discord_id=interaction.user.id)
        crate_instance = await CrateInstance.objects.select_related("player", "crate").aget(pk=self.crate_instance.pk)

        if crate_instance.player != player:
            await interaction.followup.send(f"This {settings.crate_name} no longer belongs to you.")
            return

        instances = await open_crate(crate_instance, player)
        await interaction.followup.send(
            view=await CrateResultView.build(interaction.client, interaction.user, crate_instance, instances)
        )
        await crate_instance.adelete()

        with suppress(discord.HTTPException, discord.NotFound):
            await interaction.edit_original_response(view=await CrateListView.build(interaction.user))


class CrateListView(LayoutView):
    def __init__(self, viewer: discord.User | discord.Member):
        super().__init__()
        self.viewer = viewer
        self.restrict_author(viewer.id)

    @classmethod
    async def build(
        cls, user: discord.User | discord.Member, viewer: discord.User | discord.Member | None = None
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
            text_item = discord.ui.TextDisplay(f"**{crate}** ({crate.count})")

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


class CrateResultView(LayoutView):
    def __init__(self, author: discord.User | discord.Member):
        super().__init__()
        self.restrict_author(author.id)

    @classmethod
    async def build(
        cls,
        bot: "BallsDexBot",
        author: discord.User | discord.Member,
        crate_instance: CrateInstance,
        instances: list[BallInstance],
    ) -> "CrateResultView":
        settings = await get_settings()
        view = cls(author)

        text_components = [
            discord.ui.TextDisplay(
                f"{bot.get_emoji(instance.countryball.emoji_id) or '?'} "
                f"**{instance.countryball.country}** (`#{instance.pk:x}`)"
            )
            for instance in instances
        ]

        container = await MenuContainer.build(
            discord.ui.TextDisplay(f"### {crate_instance.crate} {settings.crate_name.title()} Results"),
            discord.ui.Separator(),
            *text_components,
        )

        view.add_item(container)
        return view
