import jwt
from quart import abort
from quart.local import LocalProxy
import keys


def _get_user_id_from_session(session):
    try:
        decoded = jwt.decode(session['token'], keys.jwt_secret)
        return int(decoded['user_id'])
    except KeyError:
        return abort(401, 'Not logged in')


def _get_user_from_session(self):
    user_id = _get_user_id_from_session(self)
    return self.bot.get_user(user_id)


LocalProxy.get_user = _get_user_from_session
LocalProxy.get_user_id = _get_user_id_from_session
