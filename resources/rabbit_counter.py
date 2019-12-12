import time
from datetime import datetime

from resources import Resource


class RabbitCounter(Resource):
    __slots__ = ('count', 'summonedBy', 'summonedAt')

    def __init__(self, **kwargs):
        self.count = kwargs.pop('count', None)
        self.summonedBy = kwargs.pop('summonedBy')
        self.summonedAt = kwargs.pop('summonedAt', int(time.time()))

    @classmethod
    def convert(cls, record):
        return cls(
            count=record['count'],
            summonedBy=record['summoned_by'],
            summonedAt=datetime.fromtimestamp(record['summoned_at']),
        )

    @classmethod
    def convertMany(cls, record):
        rabbits = []
        for rabbit in record:
            rabbits.append(RabbitCounter.convert(rabbit))

        return rabbits
