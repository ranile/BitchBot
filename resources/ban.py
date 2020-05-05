from datetime import datetime

from resources import Resource


class Ban(Resource):
    def __init__(self, **kwargs):
        self.id = kwargs.pop('id', None)
        self.reason = kwargs.pop('reason', None)
        self.banned_at = kwargs.pop('banned_at', datetime.utcnow())
        self.banned_by_id = kwargs.pop('banned_by_id')
        self.banned_user_id = kwargs.pop('banned_user_id')
        self.unban_time = kwargs.pop('unban_time', None)
        self.guild_id = kwargs.pop('guild_id')

    @classmethod
    def convert(cls, record):
        return cls(
            id=record['id'],
            reason=record['reason'],
            banned_at=record['banned_at'],
            banned_by_id=record['banned_by_id'],
            banned_user_id=record['banned_user_id'],
            unban_time=record['unban_time'],
            guild_id=record['guild_id'],
        )


