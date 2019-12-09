import resources


class Emoji(resources.Resource):

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.isAnimated = kwargs.pop('isAnimated')
        self.isEpic = kwargs.pop('isEpic')
        self.id = kwargs.pop('id')

    @classmethod
    def convert(cls, record):
        return cls(
            name=record['name'],
            isAnimated=record['is_animated'],
            isEpic=record['is_epic'],
            id=record['id']
        )
