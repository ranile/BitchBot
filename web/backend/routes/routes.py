from quart import jsonify

from util import quart_fix

blueprint = quart_fix.BlueprintWithBot('my_blueprint', __name__, url_prefix='/api')


@blueprint.route("/heartbeat")
def heartbeat():
    return {"status": "healthy", 'bot': str(blueprint.bot), 'num': len(blueprint.bot.socket_stats),
            'user': str(blueprint.bot.get_user(529535587728752644))}


@blueprint.route('/icon')
async def icon():
    return jsonify(url=str(blueprint.bot.get_user(595363392886145046).avatar_url_as(size=256)))


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(blueprint, bot)
