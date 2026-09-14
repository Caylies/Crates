from typing import TYPE_CHECKING

import discord

from ...models import CrateInstance, Pool
from .shared import BaseResultView

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

__all__ = ("PoolResultView",)


class PoolResultView(BaseResultView):
    @classmethod
    async def build(
        cls, bot: "BallsDexBot", author: discord.User | discord.Member, pool: Pool, instances: list[CrateInstance]
    ):
        return await cls.build_view(
            author,
            f"{pool.name.title()} Results",
            [f"**{await instance.crate.describe(bot)}**" for instance in instances],
        )
