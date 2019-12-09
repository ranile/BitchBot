import asyncpg

from resources import Emoji
from services.emoji_service import EmojiService

connection = None


async def connect():
    global connection
    connection = await asyncpg.connect(user="postgres", password="", host="172.18.0.2", port=5432)


async def createTables():
    await connection.execute('''
    CREATE TABLE IF NOT EXISTS Emojis (
        name varchar(40),
        command varchar(40),
        is_animated bool,
        is_epic bool,
        id bigint
    );''')


async def init():
    await connect()
    await createTables()

    # service = EmojiService()
    # emoji = Emoji(
    #     name='angrythonk', command='<:angrythonk:642611216862150657>', isAnimated=True, isEpic=False,
    #     id=642611216862150657
    # )
    #
    # await service.insert(emoji)
    #
    # print([str(x) for x in await service.getAll()])


async def close():
    await connection.close()
