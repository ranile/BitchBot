import time

import asyncpg

from resources import RabbitCounter
# from services import EmojiService
from services.rabbit_service import RabbitService

connection = None


async def connect():
    global connection
    connection = await asyncpg.connect(user="postgres", password="", host="172.18.0.2", port=5432, database='bitch_bot')


async def createTables():
    await connection.execute('''
    CREATE TABLE IF NOT EXISTS Emojis (
        id bigint NOT NULL PRIMARY KEY,
        name text NOT NULL,
        command text NOT NULL,
        is_epic bool NOT NULL,
        is_animated bool NOT NULL
    );''')

    await connection.execute('''
    create table if not exists RabbitCounter
    (
        count serial not null primary key,
        summoned_by bigint not null,
        summoned_at int not null
    );
    ''')


async def yeet():
    rabbit = RabbitCounter(
        summonedAt=int(time.time()),
        summonedBy=453068315858960395
    )
    # res = await RabbitService.insert(rabbit)
    res = [str(x) for x in await RabbitService.getAll()]
    print(res)
    print(type(res))


async def init():
    await connect()
    await createTables()
    # await yeet()


async def close():
    await connection.close()
