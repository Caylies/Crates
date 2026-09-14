import random

from bd_models.models import Player

from ....models import Crate, CrateInstance, Pool


async def give_pool_crates(player: Player, pool: Pool) -> list[CrateInstance]:
    instances: list[CrateInstance] = []

    for _ in range(random.randint(pool.amount_min, pool.amount_max)):
        crate = await Crate.objects.filter(pools=pool).order_by("?").afirst()

        if not crate:
            continue

        instance = await CrateInstance.objects.acreate(player=player, crate=crate)
        instances.append(instance)

    return instances
