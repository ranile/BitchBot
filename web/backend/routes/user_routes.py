import json

import discord
from quart import session, jsonify, abort

import util
import services
from util import fetch_user_from_session

user_routes = util.BlueprintWithBot('users_blueprint', __name__, url_prefix='/api/users')
_services = {}


@user_routes.route('/me')
async def me():
    try:
        id_from_session = session['user_id']
        user = user_routes.bot.get_user(int(id_from_session))
        out = {}
        for attrib in discord.User.__slots__:
            if attrib.startswith('_') or attrib in ('system', 'bot'):
                continue
            out[attrib] = getattr(user, attrib)
    except KeyError:
        res = await fetch_user_from_session(util.make_oauth_session(token=session.get('oauth2_token')))
        out = res.json()
        if res.status_code != 200:
            return abort(res.status_code, json.dumps(out))

    mutual_guilds = user_routes.bot.get_mutual_guilds(int(out['id']))
    out['guilds'] = [{'name': guild.name, 'id': str(guild.id), 'icon': str(guild.icon_url)} for guild in mutual_guilds]
    print(out)
    return jsonify(user=out, id_from_session=session.get('user_id'))


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(user_routes, bot)
    _services['warnings'] = services.WarningsService(bot.db)
    _services['config'] = services.ConfigService(bot.db)
