from util import quart_fix

blueprint = quart_fix.BlueprintWithBot('my_blueprint', __name__)


@blueprint.route("/heartbeat")
def heartbeat():
    return {"status": "healthy", 'bot': str(blueprint.bot), 'num': len(blueprint.bot.socket_stats),
            'user': str(blueprint.bot.get_user(529535587728752644))}


@blueprint.route('/user/<int:user_id>')
async def user(user_id):
    usr = blueprint.bot.get_user(int(user_id))
    print(user_id, usr)
    return {'name': str(usr)}


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(blueprint, bot)
