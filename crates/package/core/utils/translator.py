from discord import app_commands
from discord.app_commands import TranslationContextTypes, locale_str
from discord.enums import Locale


class CrateTranslator(app_commands.Translator):
    def __init__(self, inner: app_commands.Translator, replacements: dict[str, str]):
        super().__init__()
        self.inner = inner
        self.replacements = replacements

    async def load(self) -> None:
        await self.inner.load()

    async def unload(self) -> None:
        await self.inner.unload()

    async def translate(self, string: locale_str, locale: Locale, context: TranslationContextTypes) -> str | None:
        text = string.message

        for before, after in self.replacements.items():
            text = text.replace(before, after)

        new_string = locale_str(text, **string.extras) if text != string.message else string
        return await self.inner.translate(new_string, locale, context)
