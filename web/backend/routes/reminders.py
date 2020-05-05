from quart import jsonify, session, abort

import util
from util import quart_fix

blueprint = quart_fix.BlueprintWithBot('reminders_blueprint', __name__, url_prefix='/api/reminders')


@blueprint.route('/')
async def icon():
    limit = 10
    fetched = await blueprint.bot.timers.timers_service.get_where(extras={"author_id": session.get_user_id()}, limit=limit)
    if len(fetched) == 0:
        return abort(204, "No content")
    data = []
    for reminder in fetched:
        data.append({
            'id': reminder.id,
            'text': reminder.kwargs['text'],
            'created_at': reminder.created_at,
            'expires_at': reminder.expires_at,
        })

    return jsonify(data)


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(blueprint, bot)
