import util
import quart

spa_blueprint = util.BlueprintWithBot('spa_blueprint', __name__, static_folder=None)
DIR = './web/frontend/dist/bitch-bot'


@spa_blueprint.route('/', defaults={'path': 'index.html'})
@spa_blueprint.route("/<path:path>")
def static_file(path):
    return quart.send_from_directory(DIR, path)


@spa_blueprint.errorhandler(404)
def send_index(path):
    return quart.send_from_directory(DIR, 'index.html')


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(spa_blueprint, bot)
