import discord

from ...models import CrateInstance, Pool
from .shared import BaseResultView

__all__ = ("PoolResultView",)


class PoolResultView(BaseResultView):
    @classmethod
    async def build(cls, author: discord.User | discord.Member, pool: Pool, instances: list[CrateInstance]):
        return await cls.build_view(
            author, f"{pool.name.title()} Results", [f"**{instance.crate.name}**" for instance in instances]
        )
