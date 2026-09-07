from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone

from bd_models.models import Player


class Pool(models.Model):
    name = models.CharField(max_length=32, unique=True, help_text="Name of this pool, e.g. 'daily'.")
    cooldown = models.DurationField(
        default=timedelta(days=1), help_text="Time a player must wait between claims from this pool."
    )
    enabled = models.BooleanField(default=True, help_text="Whether this pool can currently be claimed from.")

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
