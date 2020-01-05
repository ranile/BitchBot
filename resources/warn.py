class Warn:
    def __init__(self, **kwargs):
        self.reason = kwargs.pop('reason')
        self.warned_at = kwargs.pop('warned_at')
        self.warned_by_id = kwargs.pop('warned_by_id')
        self.warned_user_id = kwargs.pop('warned_user_id')