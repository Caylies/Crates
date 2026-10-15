from typing import TYPE_CHECKING

import discord
from discord.ui import Container, Item

from ballsdex.core.discord import LayoutView
from ballsdex.core.utils.menus import ItemFormatter, ListSource, Menu, dynamic_chunks, iter_to_async

from ...models import get_settings

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


class MenuContainer(Container):
    def __init__(self, *children: Item, accent_color: discord.Color | None = None):
        super().__init__(*children, accent_color=accent_color)

    @classmethod
    async def build(cls, *children: Item) -> "MenuContainer":
        settings = await get_settings()
        accent_color = None

        if settings.menu_color:
            color_str = settings.menu_color if settings.menu_color.startswith("#") else f"#{settings.menu_color}"
            accent_color = discord.Color.from_str(color_str)

        return cls(*children, accent_color=accent_color)


class BaseResultView(LayoutView):
    def __init__(self, author: discord.User | discord.Member):
        super().__init__()
        self.restrict_author(author.id)

    @classmethod
    async def build_view(cls, bot: "BallsDexBot", author: discord.User | discord.Member, title: str, items: list[str]):
        view = cls(author)

        header: list[Item] = [discord.ui.TextDisplay(f"### {title}"), discord.ui.Separator()]
        container = await MenuContainer.build(*header)
        view.add_item(container)

        chunks = await dynamic_chunks(view, iter_to_async(discord.ui.TextDisplay(item) for item in items))

        source = ListSource(chunks or [[]])
        formatter = ItemFormatter(container, position=len(header) - 1)

        menu = Menu(bot, view, source, formatter)
        await menu.init()

        return view
