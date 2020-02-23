from quart import abort


def format_guilds_for_response(guilds):
    return [{'name': guild.name, 'id': str(guild.id), 'icon': str(guild.icon_url)} for guild in guilds]


def is_mod(config, guild, user_id):
    member = guild.get_member(user_id)
    return set(x.id for x in member.roles) & set(config.mod_roles)


def get_user_id_from_session(session):
    try:
        return int(session['user_id'])
    except KeyError:
        return abort(401, 'Not logged in')
