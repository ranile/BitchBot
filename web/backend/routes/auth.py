import functools
import os

from quart import session, redirect, request, jsonify

import keys
from util import (run_in_executor, fetch_user_from_session, make_oauth_session, AUTHORIZATION_BASE_URL,
                  BlueprintWithBot,
                  API_BASE_URL, TOKEN_URL)

OAUTH2_CLIENT_ID = keys.client_id
OAUTH2_CLIENT_SECRET = keys.client_secret
OAUTH2_REDIRECT_URI = keys.redirect_uri

app = BlueprintWithBot('discord_oauth_login', __name__, url_prefix='/api/auth')

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


@app.route('/login')
async def index():
    discord_session = make_oauth_session(scopes='identify')
    authorization_url, state = discord_session.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    url = authorization_url + '&prompt=none'
    print(url)
    return jsonify(url=url)


@app.route('/callback')
async def callback():
    if (await request.values).get('error'):
        return request.values['error']
    discord_session = make_oauth_session(state=session.get('oauth2_state'))

    token = await run_in_executor(
        functools.partial(
            discord_session.fetch_token,
            TOKEN_URL,
            client_secret=OAUTH2_CLIENT_SECRET,
            authorization_response=request.url
        )
    )
    session['oauth2_token'] = token
    user = (await fetch_user_from_session(discord_session)).json()
    session['user_id'] = user['id']
    return redirect(keys.redirect_after_login_url)


@app.route('/logout')
async def logout():
    discord_session = make_oauth_session(token=session.get('oauth2_token'))
    logout_ = discord_session.post(API_BASE_URL + f'/oauth2/token/revoke', data={
        'client_id': OAUTH2_CLIENT_ID,
        'client_secret': OAUTH2_CLIENT_SECRET,
        'token': discord_session.access_token,
        'token_type_hint': 'access_token'
    }, headers={
        'Content-Type': 'application/x-www-form-urlencoded'
    })
    del session['user_id']
    return {'code': logout_.status_code, 'text': logout_.text}


def setup(bot):
    bot.quart_app.register_blueprint_with_bot(app, bot)
