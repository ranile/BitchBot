from typing import Optional

import quart

from web.backend.utils.blueprint_with_bot import BlueprintWithBot


class QuartWithBot(quart.Quart):

    def register_blueprint_with_bot(self, blueprint: BlueprintWithBot, bot, url_prefix: Optional[str] = None) -> None:
        blueprint.bot = bot
        super().register_blueprint(blueprint, url_prefix=url_prefix)
