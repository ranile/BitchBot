import jwt
from quart import abort

import keys


def format_guilds_for_response(guilds):
    return [{'name': guild.name, 'id': str(guild.id), 'icon': str(guild.icon_url)} for guild in guilds]


def is_mod(config, guild, user_id):
    member = guild.get_member(user_id)
    return set(x.id for x in member.roles) & set(config.mod_roles)


def get_user_id_from_session(session):
    try:
        decoded = jwt.decode(session['token'], keys.jwt_secret)
        return int(decoded['user_id'])
    except KeyError:
        return abort(401, 'Not logged in')


def get_guild(bp, guild_id):
    guild = bp.bot.get_guild(guild_id)
    if guild is None:
        return abort(400, 'Bot is not in the provided guild')
    return guild
