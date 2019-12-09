import resources


class Counter(resources.Resource):

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.count = kwargs.pop('count')
        self.countedBy = kwargs.pop('countedBy')

    @classmethod
    def convert(cls, record):
        return cls(
            name=record['name'],
            count=record['count'],
            countedBy=record['countedBy'],
        )
