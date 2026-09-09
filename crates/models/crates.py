from django.core.validators import MinValueValidator
from django.db import models

from bd_models.models import Ball, Player

from .pool import Pool


class Crate(models.Model):
    name = models.CharField(max_length=64, unique=True)
    reward = models.ManyToManyField(
        Ball,
        blank=True,
        help_text="The countryballs that can be given. If blank, countryballs will be chosen at random.",
    )
    amount_min = models.PositiveIntegerField(
        help_text="The minimum amount of countryballs that will be given.", validators=(MinValueValidator(1),)
    )
    amount_max = models.PositiveIntegerField(help_text="The maximum amount of countryballs that will be given.")
    openable = models.BooleanField(default=True, help_text="Whether this crate can be opened.")
    pools = models.ManyToManyField(Pool, blank=True, related_name="crates")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_max__gte=models.F("amount_min")), name="amount_max_gte_amount_min"
            ),
            models.CheckConstraint(condition=models.Q(amount_min__gte=1), name="amount_min_gte_1"),
        ]

    def __str__(self):
        return self.name


class CrateInstance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="crate_instances")
    crate = models.ForeignKey(Crate, on_delete=models.CASCADE, related_name="instances")
    earned_at = models.DateTimeField(auto_now_add=True)
