import lavalink
from quart import jsonify
from datetime import datetime
from util import quart_fix

blueprint = quart_fix.BlueprintWithBot('my_blueprint', __name__, url_prefix='/api')


@blueprint.route('/icon')
async def icon():
    return jsonify(url=str(blueprint.bot.get_user(595363392886145046).avatar_url_as(size=256)))


@blueprint.route('/stats')
async def stats():
    bot = blueprint.bot
    load_time = bot.get_cog('Jishaku').load_time
    total_seconds = (datetime.now() - load_time).total_seconds()
    days, hours, minutes, seconds = lavalink.utils.parse_time(total_seconds * 1000)
    out = []
    if days:
        out.append(f'{int(days)}:')

    out.append(f'{int(hours)}:{int(minutes)}')

    return jsonify(
        guilds=len(bot.guilds),
        channels=len(list(bot.get_all_channels())),
        users=len(bot.users),
        commands=len(list(bot.walk_commands())),
        uptime={
            'total_seconds': total_seconds,
            'human_friendly': ''.join(out),
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds
        },
    )


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(blueprint, bot)
