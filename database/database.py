import time

import asyncpg

from resources import RabbitCounter
# from services import EmojiService
from services.rabbit_service import RabbitService
from keys import db
connection = None


async def connect():
    global connection
    connection = await asyncpg.connect(
        user=db['user'], password=db['password'], host=db['host'], port=db['port'], database='bitch_bot'
    )


async def createTables():
    # await connection.execute('''
    # CREATE TABLE IF NOT EXISTS Emojis (
    #     id bigint NOT NULL PRIMARY KEY,
    #     name text NOT NULL,
    #     command text NOT NULL,
    #     is_epic bool NOT NULL,
    #     is_animated bool NOT NULL
    # );''')

    await connection.execute('''
    create table if not exists Counters
    (
        count serial not null primary key,
        name text not null,
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
    # print(res)
    # print(type(res))
    # print('---------------------------------------')
    [print(x) for x in await RabbitService.getAll()]
    # res = await RabbitService.get('count', 2)
    # print(res)
    # print(type(res))


async def init():
    await connect()
    await createTables()
    # await yeet()


async def close():
    await connection.close()
