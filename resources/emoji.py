import resources


class Emoji(resources.Resource):

    __slots__ = ('name', 'command', 'isAnimated', 'isEpic', 'id')

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.command = kwargs.pop('command')
        self.isAnimated = kwargs.pop('isAnimated')
        self.isEpic = kwargs.pop('isEpic')
        self.id = kwargs.pop('id')

    @classmethod
    def convert(cls, record):
        return cls(
            name=record['name'],
            command=record['command'],
            isAnimated=record['is_animated'],
            isEpic=record['is_epic'],
            id=record['id'],
        )

    @classmethod
    def convertMany(cls, records):
        emojis = []
        for emoji in records:
            emojis.append(Emoji.convert(emoji))

        return emojis
