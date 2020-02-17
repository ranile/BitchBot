from quart import session, jsonify, abort

import util
import services

mod_routes = util.BlueprintWithBot('mod_blueprint', __name__, url_prefix='/api/mod')
_services = {}


@mod_routes.route('/<int:guild_id>/warnings/<int:target_id>')
async def warnings(guild_id: int, target_id: int):
    try:
        user_id = int(session['user_id'])
    except KeyError:
        abort(401, 'Not logged in')
        return

    config_service: services.ConfigService = _services['config']
    config = await config_service.get(guild_id)
    member = mod_routes.bot.get_guild(guild_id).get_member(user_id)
    if config is None:
        abort(400, 'Not configured properly')
    elif not (set(x.id for x in member.roles) & set(config.mod_roles)):
        abort(403, 'Not a mod')

    warnings_service: services.WarningsService = _services['warnings']
    warns = await warnings_service.get_all(guild_id, target_id)
    return jsonify(warnings=[vars(warn) for warn in warns])


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(mod_routes, bot)
    _services['warnings'] = services.WarningsService(bot.db)
    _services['config'] = services.ConfigService(bot.db)
