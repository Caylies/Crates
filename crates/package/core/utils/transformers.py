from discord import app_commands

from ballsdex.core.utils.transformers import TTLModelTransformer

from ....models import Crate


class CrateTransformer(TTLModelTransformer[Crate]):
    name = "crate"
    model = Crate


CrateTransform = app_commands.Transform[Crate, CrateTransformer]
