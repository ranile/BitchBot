from resources import Resource


class Mute(Resource):
    def __init__(self, **kwargs):
        self.reason = kwargs.pop('reason')
        self.muted_at = kwargs.pop('muted_at')
        self.muted_by_id = kwargs.pop('muted_by_id')
        self.muted_user_id = kwargs.pop('muted_user_id')
