from resources import Resource


class Starboard(Resource):
    def __init__(self, **kwargs):
        self.message_id = kwargs.pop('message_id')
        self.id = kwargs.pop('id')
        self.started_at = kwargs.pop('started_at')
        self.message_content = kwargs.pop('message_content')
        self.attachment = kwargs.pop('attachment')
        self.stars_count = kwargs.pop('stars_count')
        self.guild = kwargs.pop('guild')
        self.channel = kwargs.pop('channel')
        self.author = kwargs.pop('author')

    @classmethod
    def convert(cls, record):
        return cls(
            message_id=record['message_id'],
            id=record['id'],
            started_at=record['started_at'],
            message_content=record['message_content'],
            attachment=record['attachment'],
            stars_count=record['stars_count'],
            guild=record['guild_id'],
            channel=record['channel_id'],
            author=record['author_id']
        )
