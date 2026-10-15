from functools import partial
from typing import TYPE_CHECKING

import discord
from query_builder_widget import evaluate
from query_builder_widget.types import EvaluationResult

from bd_models.models import Player

from ....models import Pool
from .checks import has_ball_completion, has_ball_count, has_crate_count, in_guild, is_user

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def evaluate_pool(pool: Pool, *, bot: "BallsDexBot", user: discord.User, player: Player) -> EvaluationResult:
    data = {
        "server": partial(in_guild, bot, user),
        "completion": partial(has_ball_completion, player),
        "ball_count": partial(has_ball_count, player),
        "user": partial(is_user, user),
        "total_crates": partial(has_crate_count, player),
    }

    return await evaluate(pool.conditions, data)
