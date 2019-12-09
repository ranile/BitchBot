import services
from database import database
from resources import Emoji


class EmojiService(services.Service):
    def __init__(self):
        self.connection = database.connection

    async def get(self, id):
        emoji = await self.connection.fetch("""SELECT * FROM Emojis WHERE id = $1;""", id)
        return Emoji.convert(emoji)

    async def getAll(self):
        emojis = await self.connection.fetch("""SELECT * FROM Emojis""")
        return Emoji.convertMany(emojis)

    async def insert(self, res):
        await self.connection.execute(
            """INSERT INTO Emojis VALUES ($1, $2, $3, $4, $5);""",
            res.name,
            res.command,
            res.isAnimated,
            res.isEpic,
            res.id
        )

    async def update(self, replacement):
        return await super().update(replacement)

    async def delete(self, id):
        return await super().delete(id)

    async def rawQuery(self, query, *args):
        return await self.connection.execute(query, args)
