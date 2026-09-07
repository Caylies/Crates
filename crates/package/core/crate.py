import random

from ballsdex.packages.countryballs.countryball import BallSpawnView
from ballsdex.settings import settings
from bd_models.models import BallInstance, Player, balls

from ...models import Crate, CrateInstance


async def open_crate(crate_instance: CrateInstance, player: Player) -> list[BallInstance]:
    instances: list[BallInstance] = []

    reward = [ball async for ball in crate_instance.crate.reward.all()]

    if not reward:
        reward = [x for x in balls.values() if x.enabled]

    for _ in range(random.randint(crate_instance.crate.amount_min, crate_instance.crate.amount_max)):
        ball_instance = await BallInstance.objects.acreate(
            ball=random.choice(reward),
            player=player,
            special=BallSpawnView.get_random_special(),
            attack_bonus=random.randint(-settings.max_attack_bonus, settings.max_attack_bonus),
            health_bonus=random.randint(-settings.max_attack_bonus, settings.max_attack_bonus),
        )
        instances.append(ball_instance)

    return instances


async def get_random_crate(*, pool_name: str) -> Crate | None:
    return await Crate.objects.filter(pools__name=pool_name, pools__enabled=True).order_by("?").afirst()
