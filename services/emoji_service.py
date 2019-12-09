import services
from database import database
from resources import Emoji


class EmojiService(services.Service):
    
    @classmethod
    async def get(cls, id):
        emoji = await database.connection.fetch("""SELECT * FROM Emojis WHERE id = $1;""", id)
        return Emoji.convert(emoji)

    @classmethod
    async def getAll(cls):
        emojis = await database.connection.fetch("""SELECT * FROM Emojis""")
        return Emoji.convertMany(emojis)

    @classmethod
    async def insert(cls, res):
        await database.connection.execute(
            """INSERT INTO Emojis VALUES ($1, $2, $3, $4, $5);""",
            res.name,
            res.command,
            res.isAnimated,
            res.isEpic,
            res.id
        )

    @classmethod
    async def update(cls, replacement):
        return await super().update(replacement)

    @classmethod
    async def delete(cls, id):
        return await super().delete(id)

    @classmethod
    async def rawQuery(cls, query, *args):
        return await database.connection.execute(query, args)
