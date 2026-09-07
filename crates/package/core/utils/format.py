from settings.models import settings

from ....models import get_settings


async def format_content(content: str, **extras) -> str:
    crate_settings = await get_settings()

    return content.format(
        collectibles=settings.plural_collectible_name,
        collectible=settings.collectible_name,
        discord=settings.discord_invite,
        bot=settings.bot_name,
        crates=crate_settings.plural_crate_name,
        crate=crate_settings.crate_name,
        **extras,
    )
