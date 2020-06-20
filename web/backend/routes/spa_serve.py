from web.backend.utils.blueprint_with_bot import BlueprintWithBot
import quart

spa_blueprint = BlueprintWithBot('spa_blueprint', __name__, static_folder=None)
DIR = './web/frontend/dist/bitch-bot'


@spa_blueprint.route('/', defaults={'path': 'index.html'})
@spa_blueprint.route("/<path:path>")
async def static_file(path):
    resp = await quart.send_from_directory(DIR, path)
    if resp.content_type.startswith(('text/html', 'text/css', 'application/javascript')):
        resp.cache_control.public = True
        resp.cache_control.max_age = 60 * 60
        resp.cache_control.must_revalidate = True
        resp.cache_control.no_cache = True
    elif resp.content_type.startswith('image/'):
        resp.cache_control.public = True
        resp.cache_control.max_age = 60 * 60 * 24

    return resp


@spa_blueprint.errorhandler(404)
async def send_index(path):
    resp = await quart.send_from_directory(DIR, 'index.html')
    resp.cache_control.public = True
    resp.cache_control.max_age = 60 * 60
    resp.cache_control.must_revalidate = True
    resp.cache_control.no_cache = True

    return resp


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(spa_blueprint, bot)
