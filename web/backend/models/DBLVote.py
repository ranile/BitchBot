from discord import enums


class VoteTypes(enums.Enum):
    UPVOTE = 'upvote'
    TEST = 'test'

    @classmethod
    def construct(cls, value):
        if value == 'test':
            return cls.TEST
        elif value == 'upvote':
            return cls.UPVOTE
        else:
            raise RuntimeError


class DBLVote:
    def __init__(self, *, bot, user, vote_type, is_weekend, query=None):
        self.bot_id = bot
        self.user_id = user
        self.vote_type = VoteTypes.construct(vote_type)
        self.is_weekend = is_weekend
        self.query = query

    @classmethod
    def from_dbl_json(cls, data: dict):
        return cls(
            bot=int(data.pop('bot')),
            user=int(data.pop('user')),
            vote_type=data.pop('type'),
            is_weekend=data.pop('isWeekend'),
            query=data.pop('query', None),
        )
