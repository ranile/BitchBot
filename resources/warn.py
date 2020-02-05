from datetime import datetime

from resources import Resource


class Warn(Resource):
    def __init__(self, **kwargs):
        self.id = kwargs.pop('id', None)
        self.reason = kwargs.pop('reason')
        self.warned_at = kwargs.pop('warned_at', datetime.utcnow())
        self.warned_by_id = kwargs.pop('warned_by_id')
        self.warned_user_id = kwargs.pop('warned_user_id')
        self.guild_id = kwargs.pop('guild_id')

    @classmethod
    def convert(cls, record):
        return cls(
            id=record['id'],
            reason=record['reason'],
            warned_at=record['warned_at'],
            warned_by_id=record['warned_by_id'],
            warned_user_id=record['warned_user_id'],
            guild_id=record['guild_id'],
        )
