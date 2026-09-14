import discord
from discord.ui import Container, Item

from ballsdex.core.discord import LayoutView

from ...models import get_settings


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
    async def build_view(cls, author: discord.User | discord.Member, title: str, items: list[str]):
        view = cls(author)

        container = await MenuContainer.build(
            discord.ui.TextDisplay(f"### {title}"),
            discord.ui.Separator(),
            *[discord.ui.TextDisplay(item) for item in items],
        )

        view.add_item(container)

        return view
