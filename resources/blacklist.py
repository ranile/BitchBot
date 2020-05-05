from resources import Resource


class Blacklist(Resource):
    def __init__(self, **kwargs):
        self.user_id = kwargs.pop('user_id')
        self.blacklisted_at = kwargs.pop('blacklisted_at')
        self.reason = kwargs.pop('reason')

    @classmethod
    def convert(cls, record):
        return cls(
            user_id=record['user_id'],
            blacklisted_at=record['blacklisted_at'],
            reason=record['reason'],
        )


