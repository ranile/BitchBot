import discord
import jwt
from quart import session, jsonify, abort

import keys
import util
import services

user_routes = util.BlueprintWithBot('users_blueprint', __name__, url_prefix='/api/users')
_services = {}


@user_routes.route('/me')
async def me():
    try:
        decoded = jwt.decode(session['token'], keys.jwt_secret)
    except KeyError:
        return abort(401, 'Not logged in')
    user = user_routes.bot.get_user(int(decoded['user_id']))
    out = {attrib: str(getattr(user, attrib))
           for attrib in discord.User.__slots__
           if not (attrib.startswith('_') or attrib in ('system', 'bot'))}

    out['avatar'] = str(user.avatar_url_as(static_format='png'))
    out['guilds'] = [{'name': guild.name, 'id': str(guild.id), 'icon': str(guild.icon_url)} for guild in
                     user_routes.bot.get_mutual_guilds(int(out['id']))]
    return jsonify(user=out)


@user_routes.route('/<user_id>')
async def fetch_user(user_id):
    user = user_routes.bot.get_user(int(user_id))
    if user is None:
        user = await user_routes.bot.fetch_user(int(user_id))
    user_dict = {x: getattr(user, x) for x in discord.User.__slots__ if
                 not x.startswith('_') and x not in ('system', 'bot')}
    user_dict['avatar'] = str(user.avatar_url_as(size=256))
    return user_dict


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(user_routes, bot)
    _services['warnings'] = services.WarningsService(bot.db)
    _services['config'] = services.ConfigService(bot.db)
