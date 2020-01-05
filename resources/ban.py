class Ban:
    def __init__(self, **kwargs):
        self.reason = kwargs.pop('reason')
        self.banned_at = kwargs.pop('banned_a')
        self.banned_by_id = kwargs.pop('banned_by_id')
        self.banned_user_id = kwargs.pop('banned_user_id')
        self.unban_time = kwargs.pop('unban_time')