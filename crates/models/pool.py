from datetime import datetime, timedelta

from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from bd_models.models import Player

from .regex import SLASH_COMMAND_RE


class Pool(models.Model):
    name = models.CharField(max_length=32, unique=True, help_text="Name of this pool, e.g. 'daily'.")

    amount_min = models.PositiveIntegerField(default=1, help_text="The minimum amount of crates that will be given.")
    amount_max = models.PositiveIntegerField(default=1, help_text="The maximum amount of crates that will be given.")
    enabled = models.BooleanField(default=True, help_text="Whether this pool can currently be claimed from.")

    command_name = models.CharField(
        unique=True,
        help_text="Name of this pool's claim command.",
        validators=(RegexValidator(SLASH_COMMAND_RE, message="Invalid slash command name."),),
    )

    command_description = models.CharField(max_length=100, help_text="Description of this pool's claim command.")

    cooldown = models.DurationField(
        default=timedelta(days=1), help_text="Time a player must wait between claims from this pool."
    )

    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extra requirements a player must meet to claim from this pool, on top of the cooldown.",
    )

    def __str__(self) -> str:
        return self.name


class PlayerPoolCooldown(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="pool_cooldowns")
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, related_name="player_cooldowns")
    last_claimed = models.DateTimeField()

    class Meta:
        unique_together = ("player", "pool")

    def available_at(self) -> datetime:
        return self.last_claimed + self.pool.cooldown

    def can_claim(self) -> bool:
        return timezone.now() >= self.available_at()
