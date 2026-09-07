import re

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.deconstruct import deconstructible

CACHE_KEY = "crates:settings"
SLASH_COMMAND_RE = re.compile(r"^[a-z0-9_-]{1,32}$")
HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
KEYWORDS = ("collectibles", "collectible", "discord", "bot", "crates", "crate", "name", "pool")


@deconstructible
class KeywordValidator:
    def __init__(self, *required_keys: str):
        self.required_keys = required_keys

    def __call__(self, value: str):
        try:
            value.format(**{key: "" for key in self.required_keys})
        except (KeyError, IndexError) as exc:
            raise ValidationError(
                f"This keyword must include: {', '.join('{' + key + '}' for key in self.required_keys)}"
            ) from exc


class CratesSettings(models.Model):
    crate_name = models.CharField(
        max_length=32,
        default="crate",
        help_text="The singular name of your crates",
        validators=(RegexValidator(SLASH_COMMAND_RE, message="Invalid slash command name."),),
    )
    plural_crate_name = models.CharField(
        max_length=32,
        default="crates",
        help_text="The plural name of your crates",
        validators=(RegexValidator(SLASH_COMMAND_RE, message="Invalid slash command name."),),
    )
    crates_slash_name = models.CharField(
        max_length=32,
        default="crates",
        help_text='Overrides "/crates" slash command',
        validators=(RegexValidator(SLASH_COMMAND_RE, message="Invalid slash command name."),),
    )

    menu_color = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        help_text="The accent color for view containers in hex format. Leave blank for none.",
        validators=(RegexValidator(HEX_RE, message="Invalid hex color format."),),
    )
    claim_message = models.CharField(
        max_length=256,
        default="You received one **{name}** {crate}.",
        help_text="Sent on a successful claim.",
        validators=(KeywordValidator(*KEYWORDS),),
    )

    def clean(self) -> None:
        if CratesSettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError("You can only have one instance of CratesSettings.")

    def __str__(self) -> str:
        return "Crates package settings"

    class Meta:
        verbose_name_plural = "Settings"


async def get_settings() -> CratesSettings:
    settings = cache.get(CACHE_KEY)

    if settings is None:
        settings = await CratesSettings.objects.afirst() or await CratesSettings.objects.acreate()
        cache.set(CACHE_KEY, settings, timeout=60)

    return settings
