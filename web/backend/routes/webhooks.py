import util
from quart import request, abort
import keys

from web.backend.models import DBLVote, VoteTypes
from http import HTTPStatus

blueprint = util.BlueprintWithBot('webhook_routes', __name__, url_prefix='/api/webhooks')


@blueprint.route('/dbl/vote', methods=['POST'])
async def dbl_vote():
    auth_header = request.headers['Authorization']
    if auth_header == keys.dbl_webhook_auth:
        return abort(403)

    data = DBLVote.from_dbl_json(await request.get_json())
    if data.vote_type == VoteTypes.TEST:
        print('Test')
    else:
        print('Upvote')
    print(data.bot_id, data.user_id, data.is_weekend)
    blueprint.bot.dispatch('dbl_vote', data)
    return '', HTTPStatus.OK


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(blueprint, bot)
