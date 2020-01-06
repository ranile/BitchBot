from datetime import datetime

from resources import Resource


class Mute(Resource):
    def __init__(self, **kwargs):
        self.id = kwargs.pop('id', None)
        self.reason = kwargs.pop('reason', None)
        self.muted_at = kwargs.pop('muted_at', datetime.utcnow())
        self.muted_by_id = kwargs.pop('muted_by_id')
        self.muted_user_id = kwargs.pop('muted_user_id')
        self.guild_id = kwargs.pop('guild_id')

    @classmethod
    def convert(cls, record):
        return cls(
            id=record['id'],
            reason=record['reason'],
            muted_at=record['muted_at'],
            muted_by_id=record['muted_by_id'],
            muted_user_id=record['muted_user_id'],
            guild_id=record['guild_id']
        )
