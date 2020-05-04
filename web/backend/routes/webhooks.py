import util
from quart import request, abort
import keys
import discord
from web.backend.models import DBLVote, VoteTypes
from http import HTTPStatus

blueprint = util.BlueprintWithBot('webhook_routes', __name__, url_prefix='/api/webhooks')


async def send_log_as_me(embed):
    # noinspection PyUnresolvedReferences
    log_webhook: discord.Webhook = blueprint.log_webhook
    me = blueprint.bot.user
    await log_webhook.send(embed=embed, username=str(me), avatar_url=me.avatar_url_as(format='png'))


@blueprint.route('/dbl/vote', methods=['POST'])
async def dbl_vote():
    auth_header = request.headers.get('Authorization', None)
    if auth_header is None:
        return abort(401)
    elif auth_header != keys.dbl_webhook_auth:
        return abort(403)

    data = DBLVote.from_dbl_json(await request.get_json())
    if data.vote_type == VoteTypes.TEST:
        print('Test')
    else:
        print('Upvote')
    user = blueprint.bot.get_user(data.user_id)
    fetched_user = False
    if user is None:
        user = await blueprint.bot.fetch_user(data.user_id)
        fetched_user = True

    await send_log_as_me(
        discord.Embed(title=f"{blueprint.bot.user} got an upvote on DBL {'<:weebyay:676427364871307285> ' * 3}")
        .set_author(name=user, icon_url=user.avatar_url_as(format='png'))
        .add_field(name='Weekend?', value=data.is_weekend)
        .set_footer(text='Btw, I had to fetch the user' if fetched_user else discord.Embed.Empty)
    )

    print(data.bot_id, data.user_id, data.is_weekend)
    blueprint.bot.dispatch('dbl_vote', data)
    return '', HTTPStatus.OK


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(blueprint, bot)
    blueprint.log_webhook = discord.Webhook.from_url(keys.logWebhook,
                                                     adapter=discord.AsyncWebhookAdapter(bot.clientSession))
