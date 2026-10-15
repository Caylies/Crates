import random

from django.db.models import Q

from ballsdex.packages.countryballs.countryball import BallSpawnView
from bd_models.models import Ball, BallInstance, Player, Special, balls
from settings.models import settings

from ...models import Crate, CrateInstance, SpecialBehavior


def _select_reward(reward: list[Ball], respect_rarity: bool) -> Ball:
    weights = [ball.rarity for ball in reward] if respect_rarity else None

    return random.choices(population=reward, weights=weights, k=1)[0]


def _pick_from_list(crate: Crate, specials: list[Special]) -> Special | None:
    if not specials:
        return None

    weights = [special.rarity for special in specials] if crate.respect_special_rarity else None

    return random.choices(population=specials, weights=weights, k=1)[0]


def _roll_catch_odds(specials: list[Special]) -> Special | None:
    if not specials:
        return BallSpawnView.get_random_special()

    common_weight = max(0.0, 1 - sum(special.rarity for special in specials))
    weights = [special.rarity for special in specials] + [common_weight]

    return random.choices(population=[*specials, None], weights=weights, k=1)[0]


def _select_special(crate: Crate, specials: list[Special]) -> Special | None:
    match crate.special_behavior:
        case SpecialBehavior.FROM_LIST:
            return _pick_from_list(crate, specials)
        case SpecialBehavior.CATCH_ODDS:
            return _roll_catch_odds(specials)
        case _:
            return None


async def open_crate(crate_instance: CrateInstance, player: Player) -> list[BallInstance]:
    crate = crate_instance.crate
    specials: list[Special] = []

    if crate.special_behavior != SpecialBehavior.NONE:
        specials = [special async for special in crate.specials.all()]

    reward = [ball async for ball in Ball.objects.filter(Q(crate=crate) | Q(groups__crate=crate)).distinct()]

    respect_ball_rarity = crate.respect_ball_rarity and bool(reward)

    if not reward:
        reward = [ball for ball in balls.values() if ball.enabled]

    amount = random.randint(crate.amount_min, crate.amount_max)

    instances = [
        BallInstance(
            ball=_select_reward(reward, respect_ball_rarity),
            player=player,
            special=_select_special(crate, specials),
            attack_bonus=random.randint(-settings.max_attack_bonus, settings.max_attack_bonus),
            health_bonus=random.randint(-settings.max_health_bonus, settings.max_health_bonus),
        )
        for _ in range(amount)
    ]

    return await BallInstance.objects.abulk_create(instances)
