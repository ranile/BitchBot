import services
from database import database
from resources import Emoji


class EmojiService(services.Service):

    @classmethod
    async def get(cls, name, value):
        emoji = await database.connection.fetchrow(f"""SELECT * FROM Emojis WHERE {name} = $1;""", value)
        return Emoji.convert(emoji)

    @classmethod
    async def getAll(cls):
        emojis = await database.connection.fetch("""SELECT * FROM Emojis""")
        return Emoji.convertMany(emojis)

    @classmethod
    async def insert(cls, res):
        await database.connection.execute(
            """INSERT INTO Emojis VALUES ($1, $2, $3, $4, $5);""",
            res.id,
            res.name,
            res.command,
            res.isEpic,
            res.isAnimated,
        )

    @classmethod
    async def update(cls, replacement):
        return await super().update(replacement)

    @classmethod
    async def delete(cls, id):
        return await super().delete(id)

    @classmethod
    async def rawSelectQuery(cls, query, args=()):
        fetched = await database.connection.fetch(f'''SELECT * FROM Emojis WHERE {query}''', *args)
        return Emoji.convertMany(fetched)
