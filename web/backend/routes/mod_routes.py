from quart import session, jsonify, abort, request
import util
import services

mod_routes = util.BlueprintWithBot('mod_blueprint', __name__, url_prefix='/api/mod')
_services = {}


async def _get_config(guild_id):
    config_service: services.ConfigService = _services['config']
    config = await config_service.get(guild_id)
    if config is None:
        return abort(400, 'Not configured properly')
    return config


@mod_routes.route('/<int:guild_id>/warns')
async def warnings(guild_id: int):
    user_id = util.get_user_id_from_session(session)
    guild = mod_routes.bot.get_guild(guild_id)
    if guild is None:
        return abort(400, 'Bot is not in the provided guild')

    config = await _get_config(guild.id)

    if not util.is_mod(config, guild, user_id):
        return abort(403, 'Not a mod')

    target_id = request.args.get('victim_id')
    print(target_id)
    warnings_service: services.WarningsService = _services['warnings']
    warns = await warnings_service.get_all(guild_id, target_id)
    out = []
    for warn in warns:
        out.append({
            "guild_id": str(warn.guild_id),
            "id": warn.id,
            "reason": warn.reason,
            "warned_at": int(warn.warned_at.timestamp()),
            "warned_by_id": str(warn.warned_by_id),
            "warned_user_id": str(warn.warned_user_id),
        })
    print(out)
    return jsonify(out)


@mod_routes.route('/guilds')
async def guild_i_mod():
    guilds = []
    user_id = util.get_user_id_from_session(session)
    mutual_guilds = mod_routes.bot.get_mutual_guilds(int(user_id))
    for guild in mutual_guilds:
        config = await _get_config(guild)
        if util.is_mod(config, guild, user_id):
            guilds.append(guild)

    return util.format_guilds_for_response(guilds)


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(mod_routes, bot)
    _services['warnings'] = services.WarningsService(bot.db)
    _services['config'] = services.ConfigService(bot.db)
