from typing import Optional
import quart


class BlueprintWithBot(quart.Blueprint):

    def __init__(self, name: str, import_name: str, static_folder: Optional[str] = None,
                 static_url_path: Optional[str] = None, template_folder: Optional[str] = None,
                 url_prefix: Optional[str] = None, subdomain: Optional[str] = None,
                 root_path: Optional[str] = None, bot=None) -> None:
        self.bot = bot
        super().__init__(name, import_name, static_folder, static_url_path, template_folder, url_prefix, subdomain,
                         root_path)


class QuartWithBot(quart.Quart):

    def register_blueprint_with_bot(self, blueprint: BlueprintWithBot, bot, url_prefix: Optional[str] = None) -> None:
        blueprint.bot = bot
        super().register_blueprint(blueprint, url_prefix)
