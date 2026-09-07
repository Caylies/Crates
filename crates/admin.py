from typing import TYPE_CHECKING

from django.contrib import admin
from django.db import models
from django.forms import widgets

from .models import Crate, CrateInstance, CratesSettings, Pool

if TYPE_CHECKING:
    from django.http import HttpRequest


@admin.register(Crate)
class CrateAdmin(admin.ModelAdmin):
    list_display = ("name", "amount_min", "amount_max")
    list_editable = ("amount_min", "amount_max")
    search_fields = ("name",)
    autocomplete_fields = ("reward", "pools")


@admin.register(CrateInstance)
class CrateInstanceAdmin(admin.ModelAdmin):
    list_display = ("player", "crate", "earned_at")
    list_filter = ("earned_at",)
    list_select_related = ("player", "crate")
    search_fields = ("player__discord_id", "crate__name")
    date_hierarchy = "earned_at"
    readonly_fields = ("earned_at",)


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    search_fields = ("name",)

    def has_add_permission(self, request: "HttpRequest"):
        return False

    def has_delete_permission(self, request: "HttpRequest", obj: Pool | None = None):
        return False

    def get_readonly_fields(self, request: "HttpRequest", obj: Pool | None = None):
        return [field.name for field in self.model._meta.fields] + [
            field.name for field in self.model._meta.many_to_many
        ]


@admin.register(CratesSettings)
class CratesSettingsAdmin(admin.ModelAdmin):
    save_on_top = True
    formfield_overrides = {models.TextField: {"widget": widgets.TextInput}}
    fieldsets = (
        (
            "Personalization",
            {
                "description": "Basic package personalization.",
                "fields": ("crate_name", "plural_crate_name", "crates_slash_name"),
            },
        ),
        (
            "Advanced personalization",
            {
                "description": "Advanced package personalization.",
                "fields": ("menu_color", "claim_message"),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request: "HttpRequest") -> bool:
        return super().has_add_permission(request) and not CratesSettings.objects.exists()

    def has_delete_permission(self, request: "HttpRequest", obj: CratesSettings | None = None) -> bool:
        return False
