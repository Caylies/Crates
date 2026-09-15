import random

from bd_models.models import Player

from ....models import Crate, CrateInstance, Pool


async def give_pool_crates(player: Player, pool: Pool) -> list[CrateInstance]:
    instances: list[CrateInstance] = []

    crates = [crate async for crate in Crate.objects.filter(pools=pool, rarity__gt=0)]

    if not crates:
        return instances

    weights = [crate.rarity for crate in crates]

    for _ in range(random.randint(pool.amount_min, pool.amount_max)):
        crate = random.choices(crates, weights=weights, k=1)[0]

        instance = await CrateInstance.objects.acreate(player=player, crate=crate)
        instances.append(instance)

    return instances
